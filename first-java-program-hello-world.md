---
title: "Your First Java Program: Hello, World!"
description: "Write, compile, and run your first Java program. Learn what each line does and how to fix common beginner errors."
tags: java, beginners, programming, tutorial
published: false
---

# Your First Java Program: Hello, World!

Every programmer has to start somewhere. A classic first step is asking a computer to display:

```text
Hello, World!
```

In this tutorial, you'll create a tiny Java program, compile it, and run it from a terminal.

## 1. Install a JDK

You need a **Java Development Kit (JDK)** to compile Java source code. After installing one, open a terminal (or PowerShell) and check that Java is available:

```sh
java -version
javac -version
```

Both commands should print a version. If either command is not recognized, install a JDK and make sure its `bin` directory is on your `PATH`. Restart the terminal after changing environment variables.

## 2. Create the source file

Create a file named `HelloWorld.java` and enter this code:

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

Save the file. The filename matters: because the class is `public` and named `HelloWorld`, Java expects the source file to be named `HelloWorld.java`. Java is also case-sensitive, so match the capital letters exactly.

## 3. Compile the program

In your terminal, move into the folder where you saved the file, then run:

```sh
javac HelloWorld.java
```

If compilation succeeds, `javac` creates `HelloWorld.class` in the same folder. That file contains the bytecode the Java runtime executes.

## 4. Run it

Run the class by its name, without the `.class` extension:

```sh
java HelloWorld
```

You should see:

```text
Hello, World!
```

That's your first Java program running!

## What does the code mean?

- `public class HelloWorld` declares a class named `HelloWorld`. A Java program's code lives inside classes.
- `public static void main(String[] args)` is the entry point the Java runtime looks for when starting this program.
- `System.out` refers to standard output, usually your terminal.
- `println` prints the text and then moves to a new line.
- The semicolons end Java statements, and braces `{}` mark the class and method blocks.

For now, you can think of `main` as the place where your program starts doing its work.

## Common beginner hiccups

- **`javac` is not recognized:** A JDK may not be installed, or its `bin` folder may not be on `PATH`.
- **`Could not find or load main class`:** Check that you are in the directory containing `HelloWorld.class`, and run `java HelloWorld` without an extension.
- **The public class name must match the filename:** Make sure the file is exactly `HelloWorld.java` and the class is exactly `HelloWorld`.
- **A missing semicolon error:** Check the end of `System.out.println("Hello, World!");`.

## Try changing it

Replace the message with your own:

```java
System.out.println("Hello from my first Java program!");
```

Save the file, compile it again with `javac HelloWorld.java`, and run it with `java HelloWorld`.

You’ve now created, compiled, and run a Java program. From here, you can explore variables, user input, and making decisions with `if` statements. Happy coding!
