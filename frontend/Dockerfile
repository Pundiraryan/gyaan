FROM dart:stable AS build
WORKDIR /app
COPY frontend/pubspec.* ./
RUN dart pub get
COPY frontend/ ./
RUN dart pub get
RUN dart compile exe lib/main.dart -o /app/bin/gyaan

FROM gcr.io/distroless/cc
COPY --from=build /app/bin/gyaan /usr/local/bin/gyaan
CMD ["/usr/local/bin/gyaan"]
