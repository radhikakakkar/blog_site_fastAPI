from fastapi import FastAPI, Path, Request, HTTPException, Header, Depends, status
import jwt
from typing import Optional
from pydantic import BaseModel
from pymongo import MongoClient
from model import Blog, UserLoginSchema, UserSchema, BlogUpdate
from auth.jwt_handler import signJWT
import uuid
from auth.jwt_handler import verify_jwt

# Connection to Database
#   xzrtyXB9G6y6CPjz
MONGODB_URI = "mongodb+srv://radhikakkar:xzrtyXB9G6y6CPjz@blogs.6p8uyk8.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_URI)


# api initialisation
app = FastAPI()
db = client["blogs"]
blogs_coll = db["coll"]
users_coll = db["users_coll"]


def insert_blog(blog, blog_id, user_id):
    blog_data = {
        "id": blog_id,
        "user_id": user_id,
        "title": blog.title,
        "nickname": blog.nickname,
        "media": blog.media,
        "descripion": blog.description,
        "snippet": blog.snippet,
    }
    result = blogs_coll.insert_one(blog_data)
    if result.acknowledged:
        return {"msg": "inserted document"}
    else:
        return {"msg": "inserting error"}


def print_blog(blog):
    print(blog)


def insert_user(user, user_id):
    user_data = {
        "user_id": user_id,
        "full_name": user.full_name,
        "email": user.email,
        "password": user.password,
    }

    result = users_coll.insert_one(user_data)
    if result.acknowledged:
        return {"Msg": "User Added Successfull"}
    else:
        return {"Msg": " inserting error"}


# def get_user_id(User: str = Header(...)):

#     # return {"user_id": User}
#     return User


# post request to create the blog
@app.post("/create-blog", dependencies=[Depends(verify_jwt)])
def create_blog(blog: Blog, request: Request):
    # user_id: str= get_user_id()
    # how do i get the header key value pair to check which user has created the blog, using authorizatoion token value or a new key value pair
    blog_id = str(uuid.uuid1())
    user_id = request.state.user_id
    insert_blog(blog, blog_id, user_id)
    print_blog(blog)
    return {"msg": "Post Done", "blog_id": blog_id, "user_id": user_id}


# get request to get the blog by id
@app.get("/get-blog/{blog_id}")
def get_blog(blog_id: str):
    return_blog = blogs_coll.find_one({"id": blog_id})
    if return_blog:
        print_blog(return_blog)
        return {
            "msg": "blog found",
            "blog-title": return_blog["title"],
            "snippet": return_blog["snippet"],
        }
    else:
        return {"error": "not Found"}


# create an update blog request


@app.delete("/delete-blog/{blog_id}")
def delete_blog(blog_id: int):
    return_blog = blogs_coll.find_one({"id": blog_id})
    if return_blog:
        del return_blog
        return {"msg": "blog deleted"}
    else:
        return {"Error": "blog does not exist "}


@app.post("/user/sign-up")
def sign_up(user: UserSchema):
    user_id = str(uuid.uuid1())
    insert_user(user, user_id)
    return signJWT(user.user_id)


def check_user(user: UserLoginSchema):
    # return_user = users_coll.find_one({"email": user.email})
    return_user = users_coll.find_one({"user_id": user.user_id})
    if return_user:
        return True
    else:
        return False


@app.post("/user/log-in")
def log_in(user: UserLoginSchema):
    return_user = users_coll.find_one(
        {"email": user.email}, {"password": user.password}
    )
    if return_user:
        return signJWT(user.email)
    else:
        return {"Error": "Invalid credetials"}


@app.get("/get-user-blogs", dependencies=[Depends(verify_jwt)])
def get_all_user_blogs(request: Request):
    user_id = request.state.user_id
    blogs = blogs_coll.find({"user_id": user_id})
    # if blogs:
    result = []
    for blog in blogs:
        blog.pop("_id")
        result.append(blog)
    return result


@app.patch("/edit-blog/{blog_id}", dependencies=[Depends(verify_jwt)])
def edit_blog(blog: BlogUpdate, blog_id, request: Request):
    user_id = request.state.user_id
    blog_updated_data: dict = {}
    for key, value in blog.model_dump().items():
        if value:
            blog_updated_data[key] = value
    final_blog = blogs_coll.update_one({"id": blog_id}, {"$set": blog_updated_data})
    if final_blog.acknowledged:
        # return final_blog
        return {"Msg": "Blog updated succeefully"}
    else:
        return {"Error": "Error in updating blog information"}


# Midlleware
# @app.middleware("http")
# async def custom_middleware(request: Request, call_next):

#     print("before request")

#     response = await call_next(request)


#     print("after request")

#     return response
