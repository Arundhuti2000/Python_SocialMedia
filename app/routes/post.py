from .. import models, schemas, oauth2
from fastapi import FastAPI, HTTPException, Response, status, Depends, APIRouter
from sqlalchemy .orm import Session 
from ..database import get_db
from typing import List

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db),get_current_user:int = Depends(oauth2.get_current_user)):
    posts=db.query(models.Post).all()
    print(posts)
    return posts
    # cursor.execute("""SELECT * FROM posts""")
    # posts=cursor.fetchall()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.CreatePost,db: Session = Depends(get_db), get_current_user:int = Depends(oauth2.get_current_user)):
    print(get_current_user.id)
    new_post=models.Post(user_id=get_current_user.id, **post.dict()) #unpacking the post dict to match the Post model
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
    # cursor.execute("""INSERT INTO POSTS (title, content, published, category, rating) VALUES (%s,%s, %s, %s, %s) RETURNING *""", (post.title,post.content, post.published, post.category, post.rating))
    # new_post= cursor.fetchone()
    # conn.commit()
    # return {"message": "Succesfully created a post", "title": new_post['title'], "id": new_post['id']}


@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(id:int, db: Session = Depends(get_db), get_current_user:int = Depends(oauth2.get_current_user)):
    try:
        post=db.query(models.Post).filter(models.Post.user_id==get_current_user.id).filter(models.Post.id==id).first()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
    # if post.user_id!=get_current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return post
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,))
    # post = cursor.fetchone()
    # print(post)
    # # post=find_post(id)
    

@router.delete("/{id}")
def delete_post(id:int, db: Session = Depends(get_db),  get_current_user:int = Depends(oauth2.get_current_user)):
    post_query=db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
    if post.user_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    post_query.delete(synchronize_session=False) #chooses the strategy to update the attributes on objects in the session. See the section orm_expression_update_delete for a discussion of these strategies.
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.UpdatePost, db: Session = Depends(get_db), get_current_user:int = Depends(oauth2.get_current_user)):
    post_query=db.query(models.Post).filter(models.Post.id == id)
    post= post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
    if post.user_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s, category = %s, rating = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, post.category, post.rating, id))
    # updated_post = cursor.fetchone()
    # conn.commit()