package com.example.knowledge.document;

import com.example.knowledge.document.dto.DocumentResponse;
import com.example.knowledge.document.dto.UploadDocumentRequest;
import com.example.knowledge.security.AuthenticatedUser;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    private final DocumentService service;

    public DocumentController(DocumentService service) {
        this.service = service;
    }

    @PostMapping
    public ResponseEntity<DocumentResponse> upload(
            @Valid @RequestBody UploadDocumentRequest request, Authentication authentication) {
        AuthenticatedUser user = AuthenticatedUser.from(authentication);
        return ResponseEntity.status(HttpStatus.CREATED).body(service.upload(request, user));
    }

    @GetMapping
    public List<DocumentResponse> list(Authentication authentication) {
        return service.listVisible(AuthenticatedUser.from(authentication));
    }
}
