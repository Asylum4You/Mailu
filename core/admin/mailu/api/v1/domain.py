import validators
from flask_restx import Resource, fields, marshal
from . import api, response_fields, user
from .. import common
from ... import models

db = models.db

dom = api.namespace('domain', description='Domain operations')
alt = api.namespace('alternative', description='Alternative operations')

domain_fields = api.model('Domain', {
    'name': fields.String(description='FQDN (e.g. example.com)', example='example.com', required=True),
    'comment': fields.String(description='a comment'),
    'max_users': fields.Integer(description='maximum number of users', min=-1, default=-1),
    'max_aliases': fields.Integer(description='maximum number of aliases', min=-1, default=-1),
    'max_quota_bytes': fields.Integer(description='maximum quota for mailbox', min=0),
    'signup_enabled': fields.Boolean(description='allow signup'),
    'alternatives': fields.List(fields.String(attribute='name', description='FQDN'), example='["example.com"]'),
})

domain_fields_update = api.model('DomainUpdate', {
    'comment': fields.String(description='a comment'),
    'max_users': fields.Integer(description='maximum number of users', min=-1, default=-1),
    'max_aliases': fields.Integer(description='maximum number of aliases', min=-1, default=-1),
    'max_quota_bytes': fields.Integer(description='maximum quota for mailbox', min=0),
    'signup_enabled': fields.Boolean(description='allow signup'),
    'alternatives': fields.List(fields.String(attribute='name', description='FQDN'), example='["example.com"]'),
})

domain_fields_get = api.model('DomainGet', {
    'name': fields.String(description='FQDN (e.g. example.com)', example='example.com', required=True),
    'comment': fields.String(description='a comment'),
    'managers': fields.List(fields.String(attribute='email', description='manager of domain')),
    'max_users': fields.Integer(description='maximum number of users', min=-1, default=-1),
    'max_aliases': fields.Integer(description='maximum number of aliases', min=-1, default=-1),
    'max_quota_bytes': fields.Integer(description='maximum quota for mailbox', min=0),
    'signup_enabled': fields.Boolean(description='allow signup'),
    'alternatives': fields.List(fields.String(attribute='name', description='FQDN'), example='["example.com"]'),
    'dns_autoconfig': fields.List(fields.String(description='DNS client auto-configuration entry')),
    'dns_mx': fields.String(Description='MX record for domain'),
    'dns_spf': fields.String(Description='SPF record for domain'),
    'dns_dkim': fields.String(Description='DKIM records for domain'),
    'dns_dmarc': fields.String(Description='DMARC record for domain'),
    'dns_dmarc_report': fields.String(Description='DMARC report record for domain'),
    'dns_tlsa': fields.List(fields.String(Description='TLSA records for domain')),
})

domain_fields_dns = api.model('DomainDNS', {
    'dns_autoconfig': fields.List(fields.String(description='DNS client auto-configuration entry')),
    'dns_mx': fields.String(Description='MX record for domain'),
    'dns_spf': fields.String(Description='SPF record for domain'),
    'dns_dkim': fields.String(Description='DKIM records for domain'),
    'dns_dmarc': fields.String(Description='DMARC record for domain'),
    'dns_dmarc_report': fields.String(Description='DMARC report record for domain'),
    'dns_tlsa': fields.List(fields.String(Description='TLSA records for domain')),
})

manager_fields = api.model('Manager', {
    'managers': fields.List(fields.String(attribute='email', description='manager of domain')),
})

manager_fields_create = api.model('ManagerCreate', {
    'user_email': fields.String(description='email address of manager', required=True),
})

alternative_fields_update = api.model('AlternativeDomainUpdate', {
    'domain': fields.String(description='domain FQDN', example='example.com', required=False),
})

alternative_fields = api.model('AlternativeDomain', {
    'name': fields.String(description='alternative FQDN', example='example2.com', required=True),
    'domain': fields.String(description='domain FQDN', example='example.com', required=True),
})


@dom.route('')
class Domains(Resource):
    @dom.doc('list_domain')
    @dom.marshal_with(domain_fields_get, as_list=True, skip_none=True, mask=None)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def get(self):
        """ List all domains """
        return models.Domain.query.all()

    @dom.doc('create_domain')
    @dom.expect(domain_fields)
    @dom.response(200, 'Success', response_fields)
    @dom.response(400, 'Input validation exception', response_fields)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.response(409, 'Duplicate domain/alternative name', response_fields)
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def post(self):
        """ Create a new domain """
        data = api.payload
        if not validators.domain(data['name']):
            return { 'code': 400, 'message': f'Domain {data["name"]} is not a valid domain'}, 400

        if common.fqdn_in_use(data['name']):
            return { 'code': 409, 'message': f'Duplicate domain name {data["name"]}'}, 409
        if 'alternatives' in data:
            #check if duplicate alternatives are supplied
            if [x for x in data['alternatives'] if data['alternatives'].count(x) >= 2]:
                return { 'code': 409, 'message': f'Duplicate alternative domain names in request' }, 409
            for item in data['alternatives']:
                if common.fqdn_in_use(item):
                    return { 'code': 409, 'message': f'Duplicate alternative domain name {item}' }, 409
                if not validators.domain(item):
                    return { 'code': 400, 'message': f'Alternative domain {item} is not a valid domain'}, 400
            for item in data['alternatives']:
                alternative = models.Alternative(name=item, domain_name=data['name'])
                models.db.session.add(alternative)
        domain_new = models.Domain(name=data['name'])
        if 'comment' in data:
            domain_new.comment = data['comment']
        if 'max_users' in data:
            domain_new.max_users = data['max_users']
        if 'max_aliases' in data:
            domain_new.max_aliases = data['max_aliases']
        if 'max_quota_bytes' in data:
            domain_new.max_quota_bytes = data['max_quota_bytes']
        if 'signup_enabled' in data:
            domain_new.signup_enabled = data['signup_enabled']
        models.db.session.add(domain_new)
        #apply the changes
        db.session.commit()
        return  {'code': 200, 'message': f'Domain {data["name"]} has been created'}, 200

@dom.route('/<domain>')
class Domain(Resource):

    @dom.doc('find_domain')
    @dom.response(200, 'Success', domain_fields_get)
    @dom.response(400, 'Input validation exception', response_fields)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.response(404, 'Domain not found', response_fields)
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def get(self, domain):
        """ Look up the specified domain """
        if not validators.domain(domain):
            return { 'code': 400, 'message': f'Domain {domain} is not a valid domain'}, 200
        domain_found = models.Domain.query.get(domain)
        if not domain_found:
            return { 'code': 404, 'message': f'Domain {domain} does not exist'}, 404
        return marshal(domain_found, domain_fields_get), 200

    @dom.doc('update_domain')
    @dom.expect(domain_fields_update)
    @dom.response(200, 'Success', response_fields)
    @dom.response(400, 'Input validation exception', response_fields)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.response(404, 'Domain not found', response_fields)
    @dom.response(409, 'Duplicate domain/alternative name', response_fields)
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def patch(self, domain):
        """ Update the specified domain """
        if not validators.domain(domain):
            return { 'code': 400, 'message': f'Domain {domain} is not a valid domain'}, 400
        domain_found = models.Domain.query.get(domain)
        if not domain_found:
            return { 'code': 404, 'message': f'Domain {data["name"]} does not exist'}, 404
        data = api.payload

        if 'alternatives' in data:
            #check if duplicate alternatives are supplied
            if [x for x in data['alternatives'] if data['alternatives'].count(x) >= 2]:
                return { 'code': 409, 'message': f'Duplicate alternative domain names in request' }, 409
            for item in data['alternatives']:
                if common.fqdn_in_use(item):
                    return { 'code': 409, 'message': f'Duplicate alternative domain name {item}' }, 409
                if not validators.domain(item):
                    return { 'code': 400, 'message': f'Alternative domain {item} is not a valid domain'}, 400
            for item in data['alternatives']:
                alternative = models.Alternative(name=item, domain_name=domain)
                models.db.session.add(alternative)

        if 'comment' in data:
            domain_found.comment = data['comment']
        if 'max_users' in data:
            domain_found.max_users = data['max_users']
        if 'max_aliases' in data:
            domain_found.max_aliases = data['max_aliases']
        if 'max_quota_bytes' in data:
            domain_found.max_quota_bytes = data['max_quota_bytes']
        if 'signup_enabled' in data:
            domain_found.signup_enabled = data['signup_enabled']
        models.db.session.add(domain_found)

        #apply the changes
        db.session.commit()
        return  {'code': 200, 'message': f'Domain {domain} has been updated'}, 200

    @dom.doc('delete_domain')
    @dom.response(200, 'Success', response_fields)
    @dom.response(400, 'Input validation exception', response_fields)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.response(404, 'Domain not found', response_fields)
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def delete(self, domain):
        """ Delete the specified domain """
        if not validators.domain(domain):
            return { 'code': 400, 'message': f'Domain {domain} is not a valid domain'}, 400
        domain_found = models.Domain.query.get(domain)
        if not domain_found:
            return { 'code': 404, 'message': f'Domain {domain} does not exist'}, 404
        db.session.delete(domain_found)
        db.session.commit()
        return {'code': 200, 'message': f'Domain {domain} has been deleted'}, 200

@dom.route('/<domain>/dkim')
class Domain(Resource):
    @dom.doc('generate_dkim')
    @dom.response(200, 'Success', response_fields)
    @dom.response(400, 'Input validation exception', response_fields)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.response(404, 'Domain not found', response_fields)
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def post(self, domain):
        """ Generate new DKIM/DMARC keys for the specified domain """
        if not validators.domain(domain):
            return { 'code': 400, 'message': f'Domain {domain} is not a valid domain'}, 400
        domain_found = models.Domain.query.get(domain)
        if not domain_found:
            return { 'code': 404, 'message': f'Domain {domain} does not exist'}, 404
        domain_found.generate_dkim_key()
        domain_found.save_dkim_key()
        return {'code': 200, 'message': f'DKIM/DMARC keys have been generated for domain {domain}'}, 200

@dom.route('/<domain>/manager')
class Manager(Resource):
    @dom.doc('list_managers')
    @dom.response(200, 'Success', manager_fields)
    @dom.response(400, 'Input validation exception', response_fields)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.response(404, 'domain not found', response_fields)
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def get(self, domain):
        """ List all managers of the specified domain """
        if not validators.domain(domain):
            return { 'code': 400, 'message': f'Domain {domain} is not a valid domain'}, 400
        domain_found = models.Domain.query.get(domain)
        if not domain_found:
            return { 'code': 404, 'message': f'Domain {domain} does not exist'}, 404
        return marshal(domain_found, manager_fields), 200

    @dom.doc('create_manager')
    @dom.expect(manager_fields_create)
    @dom.response(200, 'Success', response_fields)
    @dom.response(400, 'Input validation exception', response_fields)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.response(404, 'User or domain not found', response_fields)
    @dom.response(409, 'Duplicate domain manager', response_fields)
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def post(self, domain):
        """ Create a new domain manager for the specified domain """
        data = api.payload
        if not validators.email(data['user_email']):
            return {'code': 400, 'message': f'Invalid email address {data["user_email"]}'}, 400
        if not validators.domain(domain):
            return { 'code': 400, 'message': f'Domain {domain} is not a valid domain'}, 400
        domain = models.Domain.query.get(domain)
        if not domain:
            return { 'code': 404, 'message': f'Domain {domain} does not exist'}, 404
        user = models.User.query.get(data['user_email'])
        if not user:
            return { 'code': 404, 'message': f'User {data["user_email"]} does not exist'}, 404
        if user in domain.managers:
            return {'code': 409, 'message': f'User {data["user_email"]} is already a manager of the domain {domain} '}, 409
        domain.managers.append(user)
        models.db.session.commit()
        return {'code': 200, 'message': f'User {data["user_email"]} has been added as manager of the domain {domain} '},200

@dom.route('/<domain>/manager/<email>')
class Domain(Resource):
    @dom.doc('find_manager')
    @dom.response(200, 'Success', response_fields)
    @dom.response(400, 'Input validation exception', response_fields)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.response(404, 'Manager not found', response_fields)
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def get(self, domain, email):
        """ Check if the specified user is a manager of the specified domain """
        if not validators.email(email):
            return {'code': 400, 'message': f'Invalid email address {email}'}, 400
        if not validators.domain(domain):
            return { 'code': 400, 'message': f'Domain {domain} is not a valid domain'}, 400
        domain = models.Domain.query.get(domain)
        if not domain:
            return { 'code': 404, 'message': f'Domain {domain} does not exist'}, 404
        user = models.User.query.get(email)
        if not user:
            return { 'code': 404, 'message': f'User {email} does not exist'}, 404
        if user in domain.managers:
            for manager in domain.managers:
                if manager.email == email:
                    return { 'code': 200, 'message': f'User {email} is a manager of the domain {domain}'}, 200
        else:
            return { 'code': 404, 'message': f'User {email} is not a manager of the domain {domain}'}, 404


    @dom.doc('delete_manager')
    @dom.response(200, 'Success', response_fields)
    @dom.response(400, 'Input validation exception', response_fields)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.response(404, 'Manager not found', response_fields)
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def delete(self, domain, email):
        """ Delete the specified manager of the specified domain """
        if not validators.email(email):
            return {'code': 400, 'message': f'Invalid email address {email}'}, 400
        if not validators.domain(domain):
            return { 'code': 400, 'message': f'Domain {domain} is not a valid domain'}, 400
        domain = models.Domain.query.get(domain)
        if not domain:
            return { 'code': 404, 'message': f'Domain {domain} does not exist'}, 404
        user = models.User.query.get(email)
        if not user:
            return { 'code': 404, 'message': f'User {email} does not exist'}, 404
        if user in domain.managers:
            domain.managers.remove(user)
            models.db.session.commit()
            return {'code': 200, 'message': f'User {email} has been removed as a manager of the domain {domain} '},200
        else:
            return { 'code': 404, 'message': f'User {email} is not a manager of the domain {domain}'}, 404

@dom.route('/<domain>/users')
class User(Resource):
    @dom.doc('list_user_domain')
    @dom.response(200, 'Success', user.user_fields_get)
    @dom.response(400, 'Input validation exception', response_fields)
    @dom.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @dom.response(404, 'Domain not found', response_fields)
    @dom.doc(security='Bearer')
    @common.api_token_authorization
    def get(self, domain):
        """ List all the users from the specified domain """
        if not validators.domain(domain):
            return { 'code': 400, 'message': f'Domain {domain} is not a valid domain'}, 400
        domain_found = models.Domain.query.get(domain)
        if not domain_found:
            return { 'code': 404, 'message': f'Domain {domain} does not exist'}, 404
        return  marshal(models.User.query.filter_by(domain=domain_found).all(), user.user_fields_get),200

@alt.route('')
class Alternatives(Resource):

    @alt.doc('list_alternative')
    @alt.marshal_with(alternative_fields, as_list=True, skip_none=True, mask=None)
    @alt.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @alt.doc(security='Bearer')
    @common.api_token_authorization
    def get(self):
      """ List all alternatives """
      return models.Alternative.query.all()


    @alt.doc('create_alternative')
    @alt.expect(alternative_fields)
    @alt.response(200, 'Success', response_fields)
    @alt.response(400, 'Input validation exception', response_fields)
    @alt.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @alt.response(404, 'Domain not found or missing', response_fields)
    @alt.response(409, 'Duplicate alternative domain name', response_fields)
    @alt.doc(security='Bearer')
    @common.api_token_authorization
    def post(self):
        """ Create a new alternative (for domain) """
        data = api.payload
        if not validators.domain(data['name']):
            return { 'code': 400, 'message': f'Alternative domain {data["name"]} is not a valid domain'}, 400
        if not validators.domain(data['domain']):
            return { 'code': 400, 'message': f'Domain {data["domain"]} is not a valid domain'}, 400
        domain = models.Domain.query.get(data['domain'])
        if not domain:
            return { 'code': 404, 'message': f'Domain {data["domain"]} does not exist'}, 404
        if common.fqdn_in_use(data['name']):
            return { 'code': 409, 'message': f'Duplicate alternative domain name {data["name"]}'}, 409

        alternative = models.Alternative(name=data['name'], domain_name=data['domain'])
        models.db.session.add(alternative)
        db.session.commit()
        return {'code': 200, 'message': f'Alternative {data["name"]} for domain {data["domain"]} has been created'}, 200

@alt.route('/<string:alt>')
class Alternative(Resource):
    @alt.doc('find_alternative')
    @alt.doc(security='Bearer')
    @alt.response(200, 'Success', alternative_fields)
    @alt.response(400, 'Input validation exception', response_fields)
    @alt.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @alt.response(404, 'Alternative not found or missing', response_fields)
    @common.api_token_authorization
    def get(self, alt):
        """ Look up the specified alternative (of domain) """
        if not validators.domain(alt):
            return { 'code': 400, 'message': f'Alternative domain {alt} is not a valid domain'}, 400
        alternative = models.Alternative.query.filter_by(name=alt).first()
        if not alternative:
            return{ 'code': 404, 'message': f'Alternative domain {alt} does not exist'}, 404
        return marshal(alternative, alternative_fields), 200

    @alt.doc('delete_alternative')
    @alt.response(200, 'Success', response_fields)
    @alt.response(400, 'Input validation exception', response_fields)
    @alt.doc(responses={401: 'Authorization header missing', 403: 'Invalid authorization header'})
    @alt.response(404, 'Alternative/Domain not found or missing', response_fields)
    @alt.response(409, 'Duplicate domain name', response_fields)
    @alt.doc(security='Bearer')
    @common.api_token_authorization
    def delete(self, alt):
        """ Delete the specified alternative (for domain) """
        if not validators.domain(alt):
            return { 'code': 400, 'message': f'Alternative domain {alt} is not a valid domain'}, 400
        alternative = models.Alternative.query.filter_by(name=alt).scalar()
        if not alternative:
            return { 'code': 404, 'message': f'Alternative domain {alt} does not exist'}, 404
        domain = alternative.domain_name
        db.session.delete(alternative)
        db.session.commit()
        return {'code': 200, 'message': f'Alternative {alt} for domain {domain} has been deleted'}, 200
