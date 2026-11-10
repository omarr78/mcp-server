## Agent + MCP Integration

Used an AI agent powered by Dev.to MCP tools to research trending Java topics, analyze existing articles, and generate a technical blog post.

**Result:** [Read the Java 26 Blog on Dev.to](https://dev.to/omarr78/java-26-structured-concurrency-the-cancellation-boundary-your-fan-out-code-needs-f3l-temp-slug-4232796?preview=040c1738c06978bb70b64f2304422b3575a66e2383f84376018d60e1228b9db83595199265d617fdd7f83aa2773ef1b37dcc82f5b20625d89c2ad864)

**Result:** [Read Your First Java Program: Hello, World! on Dev.to](https://dev.to/omarr78/your-first-java-program-hello-world-29mp)

## Run the Dev.to MCP server in Docker

Build the image from the repository root:

```sh
docker build -t dev-blog-mcp-server .
```

The server uses stdio transport and requires a Dev.to API key. Pass the key at runtime; do not add it to the image:

```sh
docker run --rm -i -e DEVTO_API_KEY=your_devto_api_key dev-blog-mcp-server
```

When configuring an MCP client, use the image as its stdio server and pass `DEVTO_API_KEY` in the client's environment.
