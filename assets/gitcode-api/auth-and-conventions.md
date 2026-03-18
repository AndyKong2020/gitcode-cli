# Auth and Conventions

Source: <https://docs.gitcode.com/en/docs/apis/>

## Base URL and version

- Base URL: `https://api.gitcode.com`
- Current documented REST version: `/api/v5`

## Authentication

The docs introduction explicitly documents these auth forms:

- `Authorization: Bearer <token>`
- `PRIVATE-TOKEN: <token>`
- `access_token=<token>` query parameter

## Status codes

- `200 OK`: successful GET/PUT/DELETE that returns JSON
- `201 Created`: successful POST that returns the new resource
- `202 Accepted`: accepted for processing
- `204 No Content`: successful request with no response body
- `301 Moved Permanently`
- `304 Not Modified`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `405 Method Not Allowed`
- `409 Conflict`
- `412 Precondition Failed`
- `418 I'm a teapot`: request rejected as suspected unsafe
- `422 Unprocessable`
- `429 Too Many Requests`
- `500 Server Error`
- `503 Service Unavailable`
- `504 Time Out`

## Rate limits

The docs introduction states a default limit of:

- `50` requests per minute
- `4000` requests per hour
