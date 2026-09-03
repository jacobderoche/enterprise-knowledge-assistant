package com.example.knowledge.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Externalised application configuration.
 *
 * @param aiServiceBaseUrl base URL of the Python AI service
 * @param jwtSecret        HS256 shared secret used for the local/standalone JWT decoder
 * @param jwtIssuerUri     OIDC issuer URI; when set, a real IdP is used instead of the secret
 */
@ConfigurationProperties(prefix = "app")
public record AppProperties(
        String aiServiceBaseUrl,
        String jwtSecret,
        String jwtIssuerUri,
        String corsAllowedOrigins
) {
    public boolean hasIssuer() {
        return jwtIssuerUri != null && !jwtIssuerUri.isBlank();
    }

    public java.util.List<String> allowedOrigins() {
        if (corsAllowedOrigins == null || corsAllowedOrigins.isBlank()) {
            return java.util.List.of("http://localhost:3000", "http://127.0.0.1:3000");
        }
        return java.util.Arrays.stream(corsAllowedOrigins.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();
    }
}
