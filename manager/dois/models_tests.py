from datetime import datetime

from dois.models import Doi, receive_registration_email
from jobs.models import Job
from projects.models.nodes import Node

success_email = {
    "from": "CrossRef Query System <awsbounce@crossref.org>",
    "subject": "CrossRef submission ID: 1430891300",
    "text": """
<?xml version="1.0" encoding="UTF-8"?>
<doi_batch_diagnostic status="completed" sp="a-cs1">
   <submission_id>1430924839</submission_id>
   <batch_id>1@1605849946.4831526</batch_id>
   <record_diagnostic status="Success">
      <doi>10.47704/54320</doi>
      <msg>Successfully added</msg>
   </record_diagnostic>
   <batch_data>
      <record_count>1</record_count>
      <success_count>1</success_count>
      <warning_count>0</warning_count>
      <failure_count>0</failure_count>
   </batch_data>
</doi_batch_diagnostic>
""",
}

failure_email = {
    "from": "CrossRef Query System <awsbounce@crossref.org>",
    "subject": "CrossRef submission ID: 1430891300",
    "text": """
<?xml version="1.0" encoding="UTF-8"?>
<doi_batch_diagnostic status="completed" sp="a-cs1">
<submission_id>1430924840</submission_id>
<batch_id>1@1605849946.4831526</batch_id>
<record_diagnostic status="Failure">
   <doi>10.47704/54321</doi>
   <msg>Error processing relations: Relation target DOI does not exist: 10.5555/54320</msg>
</record_diagnostic>
<batch_data>
   <record_count>1</record_count>
   <success_count>0</success_count>
   <warning_count>0</warning_count>
   <failure_count>1</failure_count>
</batch_data>
</doi_batch_diagnostic>
""",
}


def test_success(db):
    article = Node.objects.create(json={})
    doi = Doi.objects.create(node=article)

    # Simulate creating a job to register the DOI
    job = doi.register()
    assert list(job.params.keys()) == ["node", "doi", "url", "batch"]

    # Simulate callback on job completion
    doi.register_callback(
        Job(
            result=dict(
                deposited="2020-11-20T22:03:57.603438Z",
                deposit_request=dict(),
                deposit_response=dict(),
                deposit_success=True,
            )
        )
    )
    assert isinstance(doi.deposited, datetime)
    assert isinstance(doi.deposit_request, dict)
    assert isinstance(doi.deposit_response, dict)
    assert doi.deposit_success is True

    # Simulate receiving response email
    receive_registration_email(None, success_email)
    doi = Doi.objects.get(id=doi.id)
    assert doi.registered is not None
    assert doi.registration_success
    assert doi.registration_response == success_email["text"]


def test_failure(db, caplog):
    article = Node.objects.create(json={})
    doi = Doi.objects.create(node=article)

    # Simulate deposit failure
    doi.register()
    doi.register_callback(Job(result=dict(deposit_success=False)))
    assert doi.deposit_success is False
    assert "Error depositing DOI" in caplog.text

    # Simulate receiving failure response email
    receive_registration_email(None, failure_email)
    doi = Doi.objects.get(id=doi.id)
    assert doi.registered is not None
    assert not doi.registration_success
    assert doi.registration_response == failure_email["text"]
    assert "Error registering DOI" in caplog.text

    # Simulate not matching batch id
    receive_registration_email(None, {"from": failure_email["from"], "text": ""})
    assert "Error registering DOI" in caplog.text
