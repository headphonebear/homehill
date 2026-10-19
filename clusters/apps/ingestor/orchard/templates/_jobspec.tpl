{{/*
╔════════════════════════════════════════════════════════════════════════════╗
║ ingestor.jobTemplate — the Job both CronJobs share (see cronjob.yaml).      ║
║ Called with (dict "root" $ "args" (list …)) so only the args differ.        ║
╚════════════════════════════════════════════════════════════════════════════╝
*/}}
{{- define "ingestor.jobTemplate" -}}
{{- $v := .root.Values.ingestor -}}
spec:
  backoffLimit: 0
  # WHY 0: no in-place retries. The next scheduled run is minutes away and
  # picks up exactly where this one stopped (the index is the state). Retries
  # would only stack Outline calls on top of a 429.
  activeDeadlineSeconds: 900
  # WHY a deadline: with concurrencyPolicy Forbid, ONE hung run (Outline or
  # Qdrant not answering) would block every following run forever. A full
  # re-embed takes ~12 s today; 15 min is generous and still unblocks.
  template:
    metadata:
      labels:
        app: ingestor
    spec:
      restartPolicy: Never
      automountServiceAccountToken: false
      # WHY: the job talks to Outline and Qdrant, never to the Kubernetes API.
      {{- with $v.image.pullSecret }}
      imagePullSecrets:
        - name: {{ . }}
      {{- end }}
      securityContext:
        runAsUser: {{ $v.uid }}
        runAsGroup: {{ $v.uid }}
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
        # WHY: see values.yaml uid (service goblin of `ai`). Same UID the image
        # declares, set here too so the pod spec says it without reading a
        # Dockerfile.
      containers:
        - name: ingestor
          image: "{{ $v.image.repository }}:{{ $v.image.tag }}"
          {{- with .args }}
          args:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          env:
            - name: OUTLINE_URL
              value: {{ $v.outline.url | quote }}
            - name: OUTLINE_TOKEN
              valueFrom:
                secretKeyRef:
                  name: {{ $v.outline.tokenSecret }}
                  key: token
            - name: QDRANT_URL
              value: {{ $v.qdrant.url | quote }}
            - name: QDRANT_API_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ $v.qdrant.keySecret }}
                  key: api-key
            - name: COLLECTION_NAME
              value: {{ $v.qdrant.collection | quote }}
            - name: OUTLINE_SKIP_SUBTREES
              value: {{ $v.skipSubtrees | quote }}
            - name: PYTHONUNBUFFERED
              value: "1"
              # WHY: print() lands in `kubectl logs` as it happens, not only
              # when the buffer flushes — matters for a run that dies midway.
            - name: HOME
              value: /tmp
              # WHY: the goblin UID has no home in the image; libraries that want
              # to write a dotfile get the tmpfs below instead of failing.
          resources:
            {{- toYaml $v.resources | nindent 12 }}
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
            # WHY read-only: tested on barn 2026-10-19 (`docker run --read-only
            # --tmpfs /tmp`, full + no-op run) — the model is baked in, offline,
            # and nothing else needs to write. /tmp is the only writable spot.
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir:
            medium: Memory
            sizeLimit: 64Mi
            # WHY in-memory + small: scratch only, counts against the memory
            # limit, gone with the pod. Nothing here is worth keeping.
{{- end -}}
