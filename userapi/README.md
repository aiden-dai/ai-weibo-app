


curl localhost:8081/api/auth -X POST -d '{"username": "abc", "password": "abc"}' --header "Content-Type: application/json"



(web) aiden@adubuntu:~/Myapps/MyRepo/ai-weibo-app$ curl -X GET localhost:8081/api/user/1{
  "data": {
    "creation_dt": "1586910454.1597748", 
    "follower": "0", 
    "following": "0", 
    "post": "0"
  }, 
  "message": "Success"
}