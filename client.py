import asyncio
import os
from dotenv import load_dotenv

from fastmcp import Client
from langchain.agents import AgentType, initialize_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.7,
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_BASE
)


@tool
async def scan_pypi_package(package_name: str, package_version: str) -> str:
    """Сканирует указанную версию Python пакета на предмет уязвимостей и предоставляет рекомендации"""
    async with Client("http://localhost:9000/mcp") as client:
        params = {"package_name": package_name, "package_version": package_version}
        data = await client.call_tool("scan_pypi_package", params)

        prompt = f"""
        Проанализируй данные об уязвимостях:
        
        {data}
        
        Предоставь структурированный анализ:
        1. Общее количество уязвимостей
        2. Классификацию по критичности (критические, высокие, средние)
        3. Краткое описание наиболее опасных уязвимостей
        4. Рекомендации по использованию/обновлению
        5. Альтернативы пакету если есть критические уязвимости
        
        Ответ представь в структурированном виде с эмодзи для наглядности.
        """

        result = await llm.ainvoke(prompt)
        return result.content


agent = initialize_agent(
    tools=[scan_pypi_package],
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
)


async def main():
    query = "Проанализируй уязвимости для пакета jinja2 версии 2.4.1"
    result = await agent.ainvoke(query)
    print(f"Результат: {result}")


if __name__ == "__main__":
    asyncio.run(main())
