curl 'https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/token' \
  -H 'authority: id.itmo.ru' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: ru' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/x-www-form-urlencoded' \
  -H 'origin: https://my.itmo.ru' \
  -H 'pragma: no-cache' \
  -H 'referer: https://my.itmo.ru/' \
  -H 'sec-ch-ua: "Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36' \
  --data-raw 'refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJjNTcxMzVjYy01ZjEwLTQ4ZTAtYTU5ZS1lYTYwMmY3ZTcxYzAifQ.eyJleHAiOjE2OTgyNjI1NzUsImlhdCI6MTY5NTY3MDU3NSwianRpIjoiNTU4YTdkOTgtNGNmZC00N2NmLWFlZmItOTFiYjUyZTc4MTg2IiwiaXNzIjoiaHR0cHM6Ly9pZC5pdG1vLnJ1L2F1dGgvcmVhbG1zL2l0bW8iLCJhdWQiOiJodHRwczovL2lkLml0bW8ucnUvYXV0aC9yZWFsbXMvaXRtbyIsInN1YiI6IjU3ZTE2NWIzLWVmNGMtNDRiYy1iNDZmLWNkZDM5ZDQ3ZTg3YSIsInR5cCI6IlJlZnJlc2giLCJhenAiOiJzdHVkZW50LXBlcnNvbmFsLWNhYmluZXQiLCJzZXNzaW9uX3N0YXRlIjoiYThmMzJiZWUtMGIzMy00YTljLTg1MjItZmUyNjZjMTllYjNhIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlZHUgd29yayIsInNpZCI6ImE4ZjMyYmVlLTBiMzMtNGE5Yy04NTIyLWZlMjY2YzE5ZWIzYSJ9.yngWe6QWfLI3i2sP0ZvA6tLu-Sy-j3kcikzuxHOYkoo&scopes=openid%20profile&client_id=student-personal-cabinet&grant_type=refresh_token' \
  --compressed
