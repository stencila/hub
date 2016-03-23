# Director

The `director` role is a Django project with several apps. A brief overview of these follows (but see the source for more complete and up to date documentation).

## Setup

The director serves raw files (using Nginx) from component repos. The component repos live in `/srv/stencila/store` and this path is hardwired into code in several places. In production this directory is setup as a NFS directory. In development you will need to create it:

```sh
sudo mkdir -p /srv/stencila/store
```

and then populate it with some component repos for testing:

```sh
cd /srv/stencila/store
git clone https://stenci.la/stencila/blog/introducing-stencils.git stencila/blog/introducing-stencils
```

and then adding a `Component` model instance for it in the admin at `/admin/components/component/` entering just its `address` (i.e. `stencila/blog/introducing-stencils`) and type (i.e `stencil`) fields.

## Deployment modes

The `director` role has several deployment modes. The `MODE` is set at the top of the `settings.py` file and determines the configuration and passwords required. The `MODE` is linked to the current repo branch. See the `settings.py` files for more details. There are some settings towards the end that may be useful to override during development using a `local_settings.py`.

## Components

The `components` app has just one model, `Component`. Components are the building blocks of Stencila. Amongst other things, each `Component` model instance...

- has an `address` which is a forward slash ('/') separated string (like a filesystem path e.g. `core/stencils/examples`).

- has "meta-" attributes `type`, `title`, `description` etc which are extracted from the component's file/s (when a component is pushed to, these fields should be updated)

- has other fields like `views` (number of page views)

- has several access and authorization related methods which mostly just call `Account.authorize()` and related methods with the component's address (see `Account` below)

- has a `tiny_url()` method for shortened URL generation/resolving

Most of the action of components is in [director/components/views.py](director/components/views.py).

The `Address` model is used for specifying the domain for authorizations. An `Address`...

- has an address string (e.g. `core/stencils/examples`). 

- is owned by an `Account`

- can be nested within another `Address` e.g. `core/stencils/examples` is within both `core` and `stencils` (see the `Address.within()` method).

- can be  `public` in which case anyone can `READ` `Component`s within that address


The `Key` and `KeyScopes` models are used for granting authorization in a manner similar to OAuth. Each `Key`...

- is linked to an `Account` and only account `owners` can create, edit or delete keys,

- is linked to one or more `users`

- has `name` and `notes` fields

- has at least one `KeyScope`


`KeyScope` models...

- grants a `right` to a `type` at an `address`. 

- all of these attributes are optional; a `KeyScope` with an empty `right`, `type` and `address` gives wholesale access to all of the accounts resources to the `Key.users`. 

The authorization logic was mostly within the `Account.authorize()` static method but has been moved to `Component.authorize()` and other places. See also `accounts.tests.test_authorize`.


## Sessions

The `sessions_` app (the name "sessions" clashed with something else) includes `Session_` and `Worker` and associated models.

`Session_` models...

- reflect Docker container instances that host a `Component` (and which communicate with the client via a "tunneled" Websocket connection)

- `start()` method assigns the session to a `Worker` and requests the worker to start the session; the `stop()` method requests the worker to stop it.

- the `monitor()` method captures information about a session and creates `SessionStats` and `SessionLogs` model instances 

`Worker` models...

- reflect virtual machines (VM) that host sessions

- communicate with [worker/worker.py](worker/worker.py) on the VM

- can be `launch()`ed (and `terminat()`ed!) on one of the `sessions_.models.platforms` (e.g. VirtualBox, EC2)

- the `update()` method captures information on the worker and stores it in a `WorkerInfo` model instance

- the `choose()` static method is for choosing which `Worker` to start a session on based on balancing requested and available compute resources (we could use some third party container orchestration toll here but having our own gives flexibility e.g. having an account type which has guaranteed compute resources versus an account type which is limited to shared, and potentially crowded compute resources)


## Users

The `users` app...

- The `UserDetails` model simply provides additional details for a user over an above what is available in `django.contrib.auth.models.User`

- The `UserToken` model allows users to authenticate using token strings (see the Authentication section below). This can be useful for non-web-browser and API access. `UserTokens` are revocable and expire after a fixed period.


## Accounts

The main models in the `accounts` app are ...

`Account` models have:

- a `type` (an instance of `AccountType`) which determines resource limits for the account (e.g. number of private components, compute time).

- one or more `User`s that are `owners`

- a `personal` flag

- `logo`, `gravatar_email` etc

All users get a personal `Account` (when the `User` instance is created). Users can create new accounts.


## Authentication

`authentication.py` implements some custom authentication backends and middleware. Alternative types of authentication are required for the different use cases:

- Basic auth: for `git` client access
- Token based: can be used as an alternative to Basic auth; similar to Github user access tokens (see `UserToken` model above)
- Permit based: session based permit which is a base64 encoded string obtained after using one of the above auth methods and visiting `user/permit`

## API

The API combines REST and RPC semantics - rather than try to shoehorn all operations into a REST model, we use RPC if it suits better. As the first comment on http://apihandyman.io/do-you-really-know-why-you-prefer-rest-over-rpc/ says:

> the best API designs incorporate a balance of REST + RPC semantics, where the usage is most appropriate. Resource-oriented design provides a big benefit in many categories, until it doesn’t. If the use case calls for it, RPC, or RPC sub-resources (under a REST collection) works out quite nicely.

The API is documented in `director/general/templates/api.yml`.

Previous incarnations of the `director` attempted to use RESTful API frameworks like `django-rest-framework` and `tastypie`. But it felt like a lot of hoops had to be jumped through to specifying particular authentication and authorization. We wanted to have Django views where it was really obvious what authorization was being done and it to be consistent across browser views, `git` client views and API views. So currently, the API is pretty much just plain old Django function based views. There is a utility module called `general/api.py` which adds some syntactic sugar to reduce the boilerplate code necessary in function based views (class based views are an alternative but have their own issues).

## Errors

Rather than trying to handle errors in views using lots of branches we try to use exceptions as much as possible. Particularly for authorization errors, you really want the model's methods to throw an exception and the view just to catch and display the exception. Also, you want the same error error messages to go to the client regardless of if it is a browser based HTML request or an AJAX JSON request. Error handling in views should be restricted to form errors. 

There is a small utility module called `general/errors.py` with a base class which defines an interface for exceptions (called class `Error`). Each derived error class should specify a `template` (for rendering in HTML) and a `serialize()` method for putting in JSON responses.
