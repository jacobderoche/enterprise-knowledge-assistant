package com.example.knowledge.security;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import org.springframework.core.convert.converter.Converter;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;

/**
 * Maps a validated JWT into Spring authorities.
 *
 * <p>The {@code roles} claim (a list of strings) becomes {@code ROLE_*}
 * authorities so that {@code @PreAuthorize("hasRole('ADMIN')")} works, and any
 * standard {@code scope}/{@code scp} claims are preserved as {@code SCOPE_*}.
 */
public class JwtAuthConverter implements Converter<Jwt, AbstractAuthenticationToken> {

    @Override
    @SuppressWarnings("unchecked")
    public AbstractAuthenticationToken convert(Jwt jwt) {
        Collection<GrantedAuthority> authorities = new ArrayList<>();

        Object roles = jwt.getClaim("roles");
        if (roles instanceof List<?> roleList) {
            for (Object role : roleList) {
                authorities.add(new SimpleGrantedAuthority("ROLE_" + String.valueOf(role).toUpperCase()));
            }
        }

        String scope = jwt.getClaimAsString("scope");
        if (scope != null) {
            for (String s : scope.split(" ")) {
                if (!s.isBlank()) {
                    authorities.add(new SimpleGrantedAuthority("SCOPE_" + s));
                }
            }
        }

        return new JwtAuthenticationToken(jwt, authorities, jwt.getSubject());
    }
}
