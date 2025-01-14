import pytest


@pytest.fixture(scope="module")
def flash_phi_handle(launcher):
    with launcher("microsoft/phi-2", num_shard=1) as handle:
        yield handle


@pytest.fixture(scope="module")
async def flash_phi(flash_phi_handle):
    await flash_phi_handle.health(300)
    return flash_phi_handle.client


@pytest.mark.asyncio
@pytest.mark.private
async def test_flash_phi(flash_phi, response_snapshot):
    response = await flash_phi.generate(
        "Test request", max_new_tokens=10, decoder_input_details=True
    )

    assert response.details.generated_tokens == 10
    assert response.generated_text == ": {request}\")\n        response = self"
    assert response == response_snapshot


@pytest.mark.asyncio
@pytest.mark.private
async def test_flash_phi_all_params(flash_phi, response_snapshot):
    response = await flash_phi.generate(
        "Test request",
        max_new_tokens=10,
        repetition_penalty=1.2,
        return_full_text=True,
        stop_sequences=["network"],
        temperature=0.5,
        top_p=0.9,
        top_k=10,
        truncate=5,
        typical_p=0.9,
        watermark=True,
        decoder_input_details=True,
        seed=0,
    )

    assert response.details.generated_tokens == 6
    assert response.generated_text == "Test request to send data over a network"
    assert response == response_snapshot


@pytest.mark.asyncio
@pytest.mark.private
async def test_flash_phi_load(flash_phi, generate_load, response_snapshot):
    responses = await generate_load(
        flash_phi, "Test request", max_new_tokens=10, n=4
    )

    assert len(responses) == 4
    assert all(
        [r.generated_text == responses[0].generated_text for r in responses]
    ), f"{[r.generated_text  for r in responses]}"
    assert responses[0].generated_text == ": {request}\")\n        response = self"

    assert responses == response_snapshot
