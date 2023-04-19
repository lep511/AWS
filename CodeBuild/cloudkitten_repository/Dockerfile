# build container stage 1
FROM public.ecr.aws/docker/library/golang:1.19.0-alpine3.16
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o bin/app .

# app container stage 2
FROM public.ecr.aws/docker/library/alpine:3.12.12
COPY --from=0 /src/bin/app app
EXPOSE 8000
CMD ["./app"]
