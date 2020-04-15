# ai-weibo-py

This repo contains a python implementation of the guestbook application (using Flask + Redis).


## Run the app locally:

1. Start redis
```bash
docker run --rm -p 6379:6379 --name my-redis -d redis
```

2. Build the docker image
```
docker build -t my-guestbook-py .
```

3. Run the guestbook app
```bash
docker run --rm -p 8080:8080 --name my-guestbook  --link my-redis:redis my-guestbook-py
```

## Run the app in kubernetes (local cluster) with Istio Ingress:

```bash
kubectl create ns demo
kubectl label ns demo istio-injection=enabled
```

- Use kubectl
```bash
kubectl config set-context --current --namespace=demo
kubectl apply -f manifests/redis.yaml
kubectl apply -f manifests/guestbook.yaml
kubectl apply -f manifests/ingress.yaml
```


- Use skaffold
```bash
# run in local-cluster
skaffold config set --global local-cluster true
skaffold run -n demo
```
