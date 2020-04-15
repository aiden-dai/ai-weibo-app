

curl localhost:8082/api/posts -X POST  --header "Content-Type: application/json" -d '
{"user_id": 1, 
"username": "aiden",
"message": "Hello world"
}
'



curl localhost:8082/api/posts -X GET
