package com.example.knowledge.security;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;

/**
 * Immutable view of the authenticated caller used to enforce permission-aware RAG.
 *
 * @param userId        JWT subject
 * @param roles         role names (lower-cased)
 * @param allowedScopes ACL scopes the user may read; always includes "public"
 */
public record AuthenticatedUser(String userId, List<String> roles, List<String> allowedScopes) {

    @SuppressWarnings("unchecked")
    public static AuthenticatedUser from(Authentication authentication) {
        if (!(authentication instanceof JwtAuthenticationToken token)) {
            throw new IllegalStateException("Expected a JWT authentication");
        }
        Jwt jwt = token.getToken();

        List<String> roles = new ArrayList<>();
        Object rolesClaim = jwt.getClaim("roles");
        if (rolesClaim instanceof List<?> list) {
            for (Object r : list) {
                roles.add(String.valueOf(r).toLowerCase());
            }
        }

        Set<String> scopes = new LinkedHashSet<>();
        scopes.add("public");
        Object scopesClaim = jwt.getClaim("scopes");
        if (scopesClaim instanceof List<?> list) {
            for (Object s : list) {
                scopes.add(String.valueOf(s));
            }
        }
        // Admins may read everything currently ingested.
        if (roles.contains("admin")) {
            scopes.add("admin");
        }

        return new AuthenticatedUser(jwt.getSubject(), roles, new ArrayList<>(scopes));
    }
}
