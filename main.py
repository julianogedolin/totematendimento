from datetime import date
from typing import Optional
from fastapi import FastAPI, status, HTTPException, Security, Query
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, validator


API_KEY = "123asd"
API_KEY_NAME = "Authorization"


api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


def get_api_key(api_key_header=Security(api_key_header_auth)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )


app = FastAPI()


class Cliente(BaseModel):
    posicao: Optional[int] = 0
    id: Optional[int] = 0
    nome: str = Query(default="", max_length=20)
    datestatus: Optional[date] = date.today()
    tipoAtendimento: str = Query(default="", max_length=1)
    status: bool = False

    @validator('tipoAtendimento')
    def valida_tipoAtendimento(cls, value: str):
        if value == "P" or value == "N":
            return value
        else:
            raise HTTPException(status_code=422, detail='"tipoAtendimento" espera "P" ou "N"')


db_clientes = [
    Cliente(posicao=1, id=1, nome="Juliano", datestatus=2022-11-25, tipoAtendimento="N", status=False),
    Cliente(posicao=2, id=2, nome="Thainara", datestatus=2022-11-25, tipoAtendimento="N", status=False),
    Cliente(posicao=3, id=3, nome="Kaique", datestatus=2022-11-26, tipoAtendimento="P", status=False),
]


@app.get("/")
async def home():
        return {"mensagem": "API de atendimento de clientes"}


@app.get("/fila", dependencies=[Security(get_api_key)])
async def exibir_fila():
    if [status == False in db_clientes]:
        return {"Clientes": [cliente for cliente in db_clientes if cliente.status == False]}
    raise HTTPException(status_code=200)


@app.get("/fila/{id}", dependencies=[Security(get_api_key)])
async def posicao_fila_cliente(id: int):
    for cliente in db_clientes:
        if cliente.posicao == id:
            return {"Cliente": [cliente for cliente in db_clientes if cliente.posicao == id]}
    raise HTTPException(status_code=404)


@app.post("/fila", dependencies=[Security(get_api_key)])
async def incluir_cliente(cliente: Cliente):
    posicoes = []
    for aux in db_clientes:
        posicoes.append(aux.posicao)
    try: 
        cliente.posicao = max(posicoes) + 1
        cliente.id = db_clientes[-1].id + 1
        cliente.datestatus = date.today()
        cliente.status = False
        db_clientes.append(cliente)
        return {"mensagem": "Cliente incluido!"}
    except:
        raise HTTPException(status_code=404)


@app.put("/fila", dependencies=[Security(get_api_key)])
async def atualizar_posicao():
    for cliente in db_clientes:
        cliente.posicao = cliente.posicao -1
        if cliente.posicao == 0:
            cliente.status = True
        if cliente.posicao < 0:
            cliente.posicao = 0
    return {"mensagem": "Fila atualizada!"}


@app.delete("/fila/{id}", dependencies=[Security(get_api_key)])
async def apagar_cliente(id: int):
    try:
        if [id == id in db_clientes]:
            cliente = [cliente for cliente in db_clientes if cliente.id == id]
            db_clientes.remove(cliente[0])
            return {"mensagem": "Cliente removido!"}
    except:
        raise HTTPException(status_code=404, detail="Cliente não localizado!")
