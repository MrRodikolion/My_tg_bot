import g4f
import asyncio

_providers = [
    # g4f.Provider.GeekGpt,
    # g4f.Provider.Phind,
    # g4f.Provider.Liaobots,
    # g4f.Provider.GptChatly,
    g4f.Provider.Llama2,
]

async def run_provider(provider: g4f.Provider.BaseProvider):
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.llama2_70b,
            messages=[{"role": "user", "content": "write a tol of text"}],
        )
        for i in response:
            print(i, end='')
        print(f"\n{provider.__name__}:", response, provider.working)
    except Exception as e:
        print(f"{provider.__name__}:", e, provider.working)


async def run_all():
    calls = [
        run_provider(provider) for provider in _providers
    ]
    await asyncio.gather(*calls)


asyncio.run(run_all())