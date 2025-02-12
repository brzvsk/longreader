FROM maven:3.8.5-openjdk-17 AS build

WORKDIR /app

COPY pom.xml ./
COPY src ./src

RUN mvn clean package

FROM openjdk:17-jdk-slim

WORKDIR /app

COPY --from=build /app/target/ReadLaterBot-1.0-SNAPSHOT.jar ./ReadLaterBot.jar

CMD ["java", "-jar", "ReadLaterBot.jar"] 