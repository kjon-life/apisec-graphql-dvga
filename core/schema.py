import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from flask import request
from flask_graphql_auth import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity
)
from rx.subject import Subject

from .models import (
    db,
    User as UserModel,
    Paste as PasteModel,
    Owner as OwnerModel,
    Audit as AuditModel,
    ServerMode as ServerModeModel
)

# Create a subject for subscriptions
paste_subject = Subject()

# SQLAlchemy Types
class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel

class Paste(SQLAlchemyObjectType):
    class Meta:
        model = PasteModel

    @staticmethod
    def resolve_ip_addr(parent, info):
        # Implement network info directive logic here
        return parent.ip_addr

class Owner(SQLAlchemyObjectType):
    class Meta:
        model = OwnerModel

class Audit(SQLAlchemyObjectType):
    class Meta:
        model = AuditModel

# Input Types
class UserInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)

# Mutations
class CreateUser(graphene.Mutation):
    class Arguments:
        user_data = UserInput(required=True)

    user = graphene.Field(lambda: User)

    def mutate(root, info, user_data=None):
        user = UserModel.create_user(**user_data)
        return CreateUser(user=user)

class CreatePaste(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        public = graphene.Boolean(default_value=False)
        burn = graphene.Boolean(default_value=False)

    paste = graphene.Field(lambda: Paste)

    def mutate(root, info, title, content, public=False, burn=False):
        # Get or create default owner
        owner = OwnerModel.query.filter_by(name='DVGAUser').first()
        if not owner:
            owner = OwnerModel(name='DVGAUser')
            db.session.add(owner)
            db.session.commit()

        paste = PasteModel.create_paste(
            title=title,
            content=content,
            public=public,
            burn=burn,
            owner_id=owner.id,
            ip_addr=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )

        # Notify subscribers
        paste_subject.on_next(paste)
        
        return CreatePaste(paste=paste)

class Login(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        password = graphene.String()

    access_token = graphene.String()
    refresh_token = graphene.String()

    def mutate(root, info, username, password):
        user = UserModel.query.filter_by(
            username=username, 
            password=password
        ).first()

        if not user:
            raise Exception('Authentication failed')

        return Login(
            access_token=create_access_token(username),
            refresh_token=create_refresh_token(username)
        )

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_paste = CreatePaste.Field()
    login = Login.Field()

# Queries
class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    
    # User queries
    users = graphene.List(User)
    user = graphene.Field(User, id=graphene.Int())
    me = graphene.Field(User)

    # Paste queries
    pastes = graphene.List(
        Paste,
        public=graphene.Boolean(),
        limit=graphene.Int()
    )
    paste = graphene.Field(
        Paste,
        id=graphene.Int(),
        title=graphene.String()
    )

    def resolve_users(root, info):
        return UserModel.query.all()

    def resolve_user(root, info, id):
        return UserModel.query.get(id)

    def resolve_me(root, info):
        username = get_jwt_identity()
        if not username:
            raise Exception('Not authenticated')
        return UserModel.query.filter_by(username=username).first()

    def resolve_pastes(root, info, public=None, limit=None):
        query = PasteModel.query
        
        if public is not None:
            query = query.filter_by(public=public)
        
        if limit:
            query = query.limit(limit)
            
        return query.all()

    def resolve_paste(root, info, id=None, title=None):
        if id:
            return PasteModel.query.get(id)
        elif title:
            return PasteModel.query.filter_by(title=title).first()
        return None

# Subscriptions
class Subscription(graphene.ObjectType):
    paste_created = graphene.Field(Paste)

    def resolve_paste_created(root, info):
        return paste_subject

# Schema
schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
) 