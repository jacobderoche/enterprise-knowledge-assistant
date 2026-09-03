package com.example.knowledge.document;

import com.example.knowledge.aiclient.AiServiceClient;
import com.example.knowledge.aiclient.dto.AiIngestRequest;
import com.example.knowledge.aiclient.dto.AiIngestResponse;
import com.example.knowledge.audit.AuditService;
import com.example.knowledge.document.dto.DocumentResponse;
import com.example.knowledge.document.dto.UploadDocumentRequest;
import com.example.knowledge.security.AuthenticatedUser;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class DocumentService {

    private final DocumentRepository documents;
    private final AiServiceClient aiClient;
    private final AuditService audit;

    public DocumentService(DocumentRepository documents, AiServiceClient aiClient, AuditService audit) {
        this.documents = documents;
        this.aiClient = aiClient;
        this.audit = audit;
    }

    @Transactional
    public DocumentResponse upload(UploadDocumentRequest request, AuthenticatedUser user) {
        String scope = request.scopeOrDefault();
        Document document = new Document(request.title(), request.source(), scope, user.userId());

        AiIngestResponse ingest = aiClient.ingest(new AiIngestRequest(
                document.getId(),
                request.source(),
                request.content(),
                scope,
                Map.of("owner", user.userId(), "title", request.title())));

        document.setChunkCount(ingest == null ? 0 : ingest.chunk_count());
        documents.save(document);

        audit.record(user.userId(), "DOCUMENT_UPLOAD", document.getId(),
                "scope=" + scope + " chunks=" + document.getChunkCount());
        return DocumentResponse.from(document);
    }

    @Transactional(readOnly = true)
    public List<DocumentResponse> listVisible(AuthenticatedUser user) {
        return documents.findByScopeInOrderByCreatedAtDesc(user.allowedScopes())
                .stream().map(DocumentResponse::from).toList();
    }
}
