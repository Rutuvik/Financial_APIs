from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .rag import index_document, search
from . import models, auth
import shutil
app = FastAPI()
Base.metadata.create_all(bind=engine)
# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# Root API 
@app.get("/")
def home():
    return {"message": "API is running"}
# AUTH
@app.post("/auth/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    user = models.User(username=username, password=password, role="Client")
    db.add(user)
    db.commit()
    return {"msg": "User created"}
@app.post("/auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_token({"username": username})
    return {"access_token": token}

# DOCUMENT API
@app.post("/documents/upload")
def upload_doc(title: str, company_name: str, document_type: str,
               file: UploadFile = File(...),
               db: Session = Depends(get_db)):

    user = db.query(models.User).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role not in ["Admin", "Analyst"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = models.Document(
        title=title,
        company_name=company_name,
        document_type=document_type,
        file_path=file_path,
        uploaded_by="user"
    )

    db.add(doc)
    db.commit()

    return {"msg": "Uploaded"}

@app.get("/documents")
def get_docs(db: Session = Depends(get_db)):
    return db.query(models.Document).all()
@app.get("/documents/{doc_id}")
def get_doc(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return doc
@app.delete("/documents/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()

    return {"msg": "Deleted"}
# METADATA SEARCH 
@app.get("/documents/search")
def search_documents(company_name: str = None, document_type: str = None,
                     db: Session = Depends(get_db)):

    query = db.query(models.Document)

    if company_name:
        query = query.filter(models.Document.company_name == company_name)

    if document_type:
        query = query.filter(models.Document.document_type == document_type)

    return query.all()
# RAG 
@app.post("/rag/index-document")
def index_doc(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    with open(doc.file_path, "r") as f:
        text = f.read()

    index_document(doc_id, text)

    return {"msg": "Indexed"}


@app.post("/rag/search")
def rag_search(query: str):
    return search(query)
# RBAC
@app.post("/roles/create")
def create_role(role_name: str, db: Session = Depends(get_db)):
    role = models.Role(name=role_name)
    db.add(role)
    db.commit()
    return {"msg": "Role created"}
@app.post("/users/assign-role")
def assign_role(user_id: int, role: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    db.commit()

    return {"msg": "Role assigned"}
@app.get("/users/{user_id}/roles")
def get_user_roles(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"role": user.role}
@app.get("/rag/context/{doc_id}")
def get_context(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    with open(doc.file_path, "r") as f:
        text = f.read()

    return {"context": text[:500]}