# General contribution guidelines

*The contribution guidelines are based on the guidelines provided by [Software and Data Carpentry](http://carpentries.org).*

[Stencila][stencila-site] is an open-source community-driven project. We encourage
and welcome contributions from all community members.

If you are comfortable with Git and GitHub, you can submit a pull request (PR). In Stencila we follow a commonly used workflow
for [contributing to open source projects][how-contribute] (see also [GitHub instructions][github-flow]).

If you have specific suggestions or have found a bug, please [create an issue](https://github.com/stencila/hub/issues/new).
If you have any issue related to security, please send us an email at security@stenci.la, rather than create a Github issue.

If you don't want to use GitHub, please tell us what you think on [our chat](https://gitter.im/stencila/stencila) on Gitter or have your say on our
our [Community Forum](https://community.stenci.la/).

## Licensing and contributor agreement

By contributing, you agree that we may redistribute your work under [our license](LICENSE).
Everyone involved with Stencila agrees to abide by our [code of conduct][conduct].

# Development

### Run `director`

To run the `director` locally:

```bash
make director-run
```

This will setup virtual environment installing all required packages. **Note** You need to have `python3` and `pip3` installed on your machine.

When you are running the `director` for the first time, you will need to set up the database for Django. For the development we use `sqlite3`. In oder to get that done:

```bash
make director-create-devdb
```
You should now be set up for development and access the development server at `http://127.0.0.1:8000/`

To run the `director` in Docker:

```bash
make director-build director-rundocker
```

**Note** This will first build the Docker file (`hub-director`) and then run director in that Docker container. If you make changes to the source code after you build the,
Docker file they will not be reflected in the container. You will have to rebuild it. Hence, it is recommended that you develop the Hub in your local environment.

### Run `editor`

To run the `editor` locally:

```bash
make editor-run
```

Or, to run the `editor` in Docker:

```bash
make editor-build editor-rundocker
```

### Run `router`

The `router` is configured to listen on port 3000 (to avoid clashing with other web servers which may already be listening to port 80)

```bash
make router-build router-rundocker
```

Now, you should be able to access the the Hub at http://localhost:3000.



## Get in touch!

You can chat with the team at our [community forum][community-forum],
on Twitter [@Stencila][stencila-twitter],
[Gitter][stencila-gitter], or email to [hello@stenci.la][contact]

[contact]: mailto:hello@stenci.la
[conduct]: https://github.com/stencila/policies/blob/master/CONDUCT.md
[github-flow]: https://guides.github.com/introduction/flow/
[github-join]: https://github.com/join
[issues]: https://help.github.com/articles/creating-an-issue/
[how-contribute]: https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github
[stencila-site]: http://stenci.la/
[stencila-repo]: https://github.com/stencila/stencila
[stencila-twitter]: https://twitter.com/stencila
[stencila-gitter]: https://gitter.im/stencila/stencila/
