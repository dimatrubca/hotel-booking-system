FROM mcr.microsoft.com/dotnet/sdk:3.1-bionic AS build-env
WORKDIR /source

# Copy csproj and restore as distinct layers
COPY ./Gateway/*.csproj ./
RUN dotnet restore

# Copy everything else and build
COPY ./Gateway/ ./Gateway
WORKDIR /source/Gateway
RUN dotnet publish -c Release -o /app

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:3.1-bionic
WORKDIR /app
COPY --from=build-env /app ./
RUN mkdir -p /app/Logs

ENTRYPOINT ["dotnet", "Gateway.dll"]