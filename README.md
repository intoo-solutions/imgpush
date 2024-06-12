<img width="246" alt="Screenshot 2019-06-19 at 17 56 29" src="https://user-images.githubusercontent.com/2439255/59781204-a23da780-92bb-11e9-99c5-490feecca557.png">

Minimalist Self-hosted File Service for user submitted files in your app (e.g. avatars).

## Features

- One simple API endpoint for uploading files
- Automatic Conversion to an image format of your choice
- Automatic resizing to any size of your liking
- Built-in Rate limiting
- Built-in Allowed Origin whitelisting
- Liveness API
- Configurable allowed file types
- Choose between S3 or file system storage

## Local Development

When developing locally, you can use the `docker-compose.yml` file to start the service. This will start the service on port 5000. To configure the service, you can copy the `.env.example` file to `.env` and adjust the settings to your liking.

```bash
wsl -e cp .env.example .env
```

To start the service, run:

```bash
wsl -e docker compose up
```

## Import files

### Using AWS CLI (only works with AWS S3)

If you want to migrate from using the file system to S3, you can use the AWS CLI to copy the files to S3. The command to copy the files is:

```bash
aws s3 cp SOURCE_DIR s3://DEST_BUCKET/ --recursive
```

### Using rclone

If you are using another provider than AWS, using the AWS CLI is not an option. In this case, you can use `rclone` to copy the files to your provider.

#### Configuring rclone

First, you will need to configure rclone to use your provider. You can do this by running:

```bash
rclone config
```

This will open a wizard that will guide you through the configuration process.
Some providers may require additional configuration, or specific options. You will find more information on their documentation. For example, Cloudflare R2 has [this documentation page](https://developers.cloudflare.com/r2/examples/rclone/) that explains how to configure rclone for Cloudflare R2.

#### Copying the files

Then, you can copy the files using the following command:

```bash
rclone copy SOURCE_DIR PROVIDER_NAME:PATH
```

For example, if you're using R2 and added a configuration named `r2`, you can copy the files using:

```bash
rclone copy /path/to/file r2:/bucket-name/subfolder --recursive # for Cloudflare R2
```

> [!WARNING]  
> Only append `/bucket-name` if the endpoint you configured in rclone doesn't already contain it. If it does, you should remove it from the path, as it would otherwise create a subfolder with the bucket name inside of your bucket.

## Usage

Uploading a file:

```bash
> curl -F 'file=@/some/file.jpg' http://some.host
{"filename":"somename.png"}
```

Fetching a file in a specific size(e.g. 320x240):

```
http://some.host/somename.png?w=320&h=240
```

returns the image cropped to the desired size

Deleting a file : `DELETE http://some.host/somename.png`. Beware, no restriction on this url, you need to restrict it yourself

## Running

imgpush requires docker to run. You can start the service by running the following command:

### Using the file system

```bash
docker run -v <PATH TO STORE FILES>:/files -p 5000:5000 intoo/imgpush:latest
```

### Using S3

```bash
docker run -e S3_ENDPOINT=https://my-s3:9000 -e S3_ACCESS_KEY_ID=accesskey -e S3_SECRET_ACCESS_KEY=secretkey -e S3_BUCKET_NAME=mybucket intoo/imgpush:latest -v <PATH TO STORE METRICS FILE>:/metrics
```

If you are using S3, you need to also start the metrics-rebuilder, which takes care of building the metrics file from an existing bucket. This is only needed if you plan on using the `/metrics` endpoint.

```bash
docker run -e REBUILD_METRICS=true -e S3_ENDPOINT=https://my-s3:9000 -e S3_ACCESS_KEY_ID=accesskey -e S3_SECRET_ACCESS_KEY=secretkey -e S3_BUCKET_NAME=mybucket intoo/imgpush:latest -v <PATH TO STORE METRICS FILE>:/metrics
```

### Kubernetes

> This is fully optional and is only needed if you want to run imgpush in Kubernetes.

If you want to deploy imgpush in Kubernetes, there is an example deployment available in the Kubernetes directory.
In case you do not have a running Kubernetes cluster yet, you can use [Minikube](https://kubernetes.io/docs/setup/) to setup a local single-node Kubernetes cluster.
Otherwise you can just use your existing cluster.

1. Verify that your cluster works:

```
$ kubectl get pods
# Should return without an error, maybe prints information about some deployed pods.
```

2. Apply the `kubernetes/deployment-example.yaml` file:

```
$ kubectl apply -f kubernetes/deployment-example.yaml
namespace/imgpush created
deployment.apps/imgpush created
persistentvolumeclaim/imgpush created
service/imgpush created
```

3. It will take a moment while your Kubernetes downloads the current imgpush image.
4. Verify that the deployment was successful:

```
$ kubectl -n imgpush get deployments.
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
imgpush   1/1     1            1           3m41s

$ kubectl -n imgpush get svc
NAME      TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)    AGE
imgpush   ClusterIP   10.10.10.41   <none>        5000/TCP   3m57s
```

5. When the deployment is finished, the READY column should be `1/1`.
6. Afterwards you can forward the port to your local machine and upload a file via your webbrowser (visit http://127.0.0.1:5000/).

```
$ kubectl -n imgpush port-forward service/imgpush 5000
Forwarding from 127.0.0.1:5000 -> 5000
Handling connection for 5000
Handling connection for 5000
Handling connection for 5000
Handling connection for 5000
```

7. To expose imgpush to the internet you need to configure an [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/). The exact configuration depends on you cluster but you can find an example in the `kubernetes/deployment-example.yaml` file that you can adapt to your setup.

### Liveness

imgpush provides the `/liveness` endpoint that always returns `200 OK` that you can use for docker Healthcheck and kubernetes liveness probe.

For Docker, as `curl` is install in the image :

```yaml
healthcheck:
  start_period: 0s
  test:
    ["CMD-SHELL", "curl localhost:5000/liveness -s -f -o /dev/null || exit 1"]
  interval: 30s
```

For Kubernetes

```yaml
livenessProbe:
  httpGet:
  path: /liveness
  port: 5000
  initialDelaySeconds: 5
  periodSeconds: 30
```

## Configuration

| Setting                  | Default value                              | Description                                                                                                                                       |
| ------------------------ | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| OUTPUT_TYPE              | Same as Input file                         | An image type supported by imagemagick, e.g. png or jpg                                                                                           |
| MAX_SIZE_MB              | "16"                                       | Integer, Max size per uploaded file in megabytes                                                                                                  |
| MAX_UPLOADS_PER_DAY      | "1000"                                     | Integer, max per IP address                                                                                                                       |
| MAX_UPLOADS_PER_HOUR     | "100"                                      | Integer, max per IP address                                                                                                                       |
| MAX_UPLOADS_PER_MINUTE   | "20"                                       | Integer, max per IP address                                                                                                                       |
| ALLOWED_ORIGINS          | "['*']"                                    | array of domains, e.g ['https://a.com']                                                                                                           |
| VALID_SIZES              | Any size                                   | array of integers allowed in the h= and w= parameters, e.g "[100,200,300]". You should set this to protect against being bombarded with requests! |
| NAME_STRATEGY            | "randomstr"                                | `randomstr` for random 5 chars, `uuidv4` for UUIDv4                                                                                               |
| ALLOWED_MIME_FILE_TYPES  | "['image/png', 'image/jpeg', 'image/jpg']" | array of allowed file types, e.g. `['image/png', 'image/jpeg', 'image/jpg']`                                                                      |
| RESIZABLE_MIME_FILE_TYPES | "['image/png', 'image/jpeg', 'image/jpg']" | array of file types that will be treated as images, and therefore resized, e.g. `['image/png', 'image/jpeg', 'image/jpg']`                        |
| S3_ENDPOINT              | ""                                         | S3 endpoint, e.g. `http://my-s3:9000`                                                                                                             |
| S3_ACCESS_KEY_ID         | ""                                         | S3 access key identifier                                                                                                                          |
| S3_SECRET_ACCESS_KEY     | ""                                         | S3 secret access key                                                                                                                              |
| S3_BUCKET_NAME           | ""                                         | S3 bucket name                                                                                                                                    |
| METRICS_FILE_PATH        | "/metrics/metrics.json"                    | Path to the file where the metrics are stored (only applicable when using S3)                                                                     |

Setting configuration variables is all set through env variables that get passed to the docker container.

### Example:

```
docker run -e ALLOWED_ORIGINS="['https://a.com', 'https://b.com']" -s -v <PATH TO STORE FILES>:/files -p 5000:5000 intoo/imgpush:latest
```

or to quickly deploy it locally, run

```
docker-compose up -d
```
