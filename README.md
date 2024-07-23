# Iris Email Analyzer

## Installing and Running the Application as a Docker Image

- Switch to the directory or folder you want this repo to be cloned into and run this clone command.

```
git clone https://github.com/ericmariasis/iris-email-analyzer-app.git
```

- Then switch into the root directory of the repo.

```
cd iris-email-analyzer-app
```

- On Docker desktop or any other terminal where you have access to Docker commands, run the below command to build the docker compose file.

```
docker compose build
```

- Once that is finished run the docker compose.

```
docker compose up -d
```

### Preparing to run the app

If you want to run the core part of the app properly, you will need to use a valid OpenAI API key. The llama-index package is used and needs the token to function properly. However, the application gracefully deals with the absence of a token by reporting the result as either `You do not have an API token` if you don't have any and it reports an invalid token as well.

To get an OpenAI API key if you don't already have one, go to [this page](https://platform.openai.com/docs/quickstart/step-2-set-up-your-api-key) to learn how to get one.

### Run the app

Run the below command, again in a terminal with Docker access, to run an iris shell.

```
docker compose exec iris bash
```

