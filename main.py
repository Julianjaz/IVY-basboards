import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from src.app.use_cases.user_assistance import UserAssistance
from src.app.use_cases.supplier_assistance import SupplierAssistance
from src.app.configs.payloads import UserPayload, TextPayload, MakeDescription
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen (puedes restringirlo si es necesario)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

@app.get("/")
def read_root():
    return {"message": "bye"}

@app.post("/user_package")
def get_recommendation(payload: UserPayload):
    return UserAssistance().get_response(payload)

@app.post("/get_best_description")
def get_best_description(payload: TextPayload):
    return SupplierAssistance().get_response(payload.text)

@app.post('/make_description')
def make_description(payload: MakeDescription):
    try: 
        return SupplierAssistance().make_description(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {e}")

#---------------------------------------------------------
@app.post('/test')
async def make_description(request: Request):
    data = await request.json()
    print(data)
    return data

class DataModel(BaseModel):
    name: str  # Campo obligatorio

@app.post("/data")
def receive_data(data: DataModel):
    try:
        if not data.name.strip():
            raise HTTPException(status_code=400, detail="El campo 'name' no puede estar vacío.")
        return {"received": data}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor.")
    
#---------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Usar la variable PORT que asigna Railway
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
