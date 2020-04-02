from unittest import TestCase

from projects.source_forms import GithubSourceForm


class TestGithubSourceForm(TestCase):
    def _get_form_data(self, **kwargs) -> dict:
        return {
            "repo": kwargs.get("repo", "user/repo"),
            "subpath": kwargs.get("subpath", "."),
            "path": kwargs.get("path", "path_in_repo"),
        }

    def test_valid_github_repo_only(self):
        """
        Test with a valid short repo identifier (`user/repo`).

        If a repository only is provided (i.e. `user/repo` rather then full URL) then that repo should be in the cleaned
        data.
        """
        f = GithubSourceForm(self._get_form_data(repo="username/reponame"))
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data["repo"], "username/reponame")

    def test_valid_github_http_url(self):
        """
        Test using the full HTTP Github URL. The username and repo should be the cleaned data.
        """
        f = GithubSourceForm(
            self._get_form_data(repo="http://github.com/myname/therepo")
        )
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data["repo"], "myname/therepo")

    def test_valid_github_http_url_trailing_slash(self):
        """
        Test using the full HTTP Github URL with a trailing /. The username and repo should be in the cleaned data.
        """
        f = GithubSourceForm(
            self._get_form_data(repo="http://github.com/some-username/the-3repo/")
        )
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data["repo"], "some-username/the-3repo")

    def test_valid_github_https_url(self):
        """
        Test using the full HTTPS Github URL. The username and repo should be the cleaned data.
        """
        f = GithubSourceForm(
            self._get_form_data(repo="https://github.com/other-username/the-4repo")
        )
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data["repo"], "other-username/the-4repo")

    def test_valid_github_https_url_trailing_slash(self):
        """
        Test using the full HTTPS Github URL with a trailing /. The username and repo should be in the cleaned data.
        """
        f = GithubSourceForm(
            self._get_form_data(repo="https://github.com/valid-6/the-5repo/")
        )
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data["repo"], "valid-6/the-5repo")

    def test_valid_github_url_no_scheme(self):
        """Test using a URL without a scheme (i.e. `github.com/user/repo`)."""
        f = GithubSourceForm(
            self._get_form_data(repo="github.com/reallygood/someproject")
        )
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data["repo"], "reallygood/someproject")

    def test_valid_github_url_no_scheme_trailing_slash(self):
        """Test using a URL without a scheme and trailing / (i.e. `github.com/user/repo/`)."""
        f = GithubSourceForm(self._get_form_data(repo="github.com/valid-8/the-8repo/"))
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data["repo"], "valid-8/the-8repo")

    def test_invalid_github_repo_bad_characters(self):
        """
        If a github repo is invalid due to containing bad characters it should raise `ValidationError` during clean.
        """
        f = GithubSourceForm(
            self._get_form_data(repo="http://github.com/my$name/ther&epo")
        )
        self.assertFalse(f.is_valid())

    def test_invalid_github_repo_too_many_components(self):
        """
        If a github repo is invalid due to having too many components it should raise `ValidationError` during clean.
        """
        f = GithubSourceForm(
            self._get_form_data(
                repo="https://github.com/valid-8/the-8repo/anothercomponent"
            )
        )
        self.assertFalse(f.is_valid())

    def test_invalid_github_repo_wrong_scheme(self):
        """
        If a github repo is invalid due to having non http(s) scheme, it should raise a `ValidationError` during clean.
        """
        f = GithubSourceForm(
            self._get_form_data(repo="ftp://github.com/valid-8/the-8repo")
        )
        self.assertFalse(f.is_valid())

    def test_invalid_github_repo_wrong_host(self):
        """
        If a github repo has a hostname other than 'github.com' it is not valid
        """
        f = GithubSourceForm(
            self._get_form_data(repo="https://notgithub.com/valid-8/the-8repo")
        )
        self.assertFalse(f.is_valid())
