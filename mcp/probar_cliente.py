import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def main():
    transporte = StreamableHttpTransport(
        "http://127.0.0.1:8001/mcp",
        headers={"x-student-code": "U00112048"}
    )

    async with Client(transporte) as cliente:
        for herramienta, argumentos in [
            ("consultar_horario", {}),
            ("consultar_asignatura", {"codigo_asignatura": "IB26-S04-03"}),
            ("buscar_profesor_por_nombre", {"nombre": "Felipe Ramírez Ortiz"})
        ]:
            print(f"\n--- {herramienta} ---")
            resultado = await cliente.call_tool(herramienta, argumentos)

            for contenido in resultado.content:
                if hasattr(contenido, "text"):
                    print(contenido.text)

asyncio.run(main())
