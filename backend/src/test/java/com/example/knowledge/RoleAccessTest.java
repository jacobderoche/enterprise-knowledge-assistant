package com.example.knowledge;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.knowledge.aiclient.AiServiceClient;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class RoleAccessTest {

    @Autowired
    MockMvc mockMvc;

    @MockBean
    AiServiceClient aiClient;

    @Test
    void employeeCannotAccessAdminAuditTrail() throws Exception {
        mockMvc.perform(get("/api/admin/audit").with(jwt()
                        .jwt(j -> j.subject("u1").claim("roles", List.of("employee")))
                        .authorities(new SimpleGrantedAuthority("ROLE_EMPLOYEE"))))
                .andExpect(status().isForbidden());
    }

    @Test
    void adminCanAccessAdminAuditTrail() throws Exception {
        mockMvc.perform(get("/api/admin/audit").with(jwt()
                        .jwt(j -> j.subject("admin1").claim("roles", List.of("admin")))
                        .authorities(new SimpleGrantedAuthority("ROLE_ADMIN"))))
                .andExpect(status().isOk());
    }

    @Test
    void userWithoutRequiredRoleCannotListDocuments() throws Exception {
        mockMvc.perform(get("/api/documents").with(jwt()
                        .jwt(j -> j.subject("g1").claim("roles", List.of("guest")))
                        .authorities(new SimpleGrantedAuthority("ROLE_GUEST"))))
                .andExpect(status().isForbidden());
    }
}
