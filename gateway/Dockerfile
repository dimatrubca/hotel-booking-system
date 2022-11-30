FROM mcr.microsoft.com/dotnet/sdk:3.1-bionic AS build-env
WORKDIR /app

# Copy csproj and restore as distinct layers
COPY ./Gateway/*.csproj ./
RUN dotnet restore

# Copy everything else and build
COPY ./Gateway ./
RUN dotnet publish -c Release -o out

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:3.1-bionic
WORKDIR /app
COPY --from=build-env /app/out .
ENTRYPOINT ["dotnet", "Gateway.dll"]