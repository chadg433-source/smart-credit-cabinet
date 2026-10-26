import { useCallback, useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { api } from '../api/client';

type Attachment = {
  id: string;
  filename: string;
  description: string | null;
  uploaded_at: string;
  status: string;
};

type Props = {
  applicationId: string;
  onUploaded?: () => void;
};

export const ApplicationAttachments = ({
  applicationId,
  onUploaded,
}: Props) => {
  const [file, setFile] = useState<File | null>(null);
  const [description, setDescription] = useState('');
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const loadAttachments = useCallback(async () => {
    return api.getApplicationAttachments(applicationId);
  }, [applicationId]);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const result = await loadAttachments();

        if (!cancelled) {
          setAttachments(result);
          setError('');
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Не удалось загрузить список документов.',
          );
        }
      } finally {
        if (!cancelled) {
          setListLoading(false);
        }
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, [loadAttachments]);

  const handleUpload = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    const form = event.currentTarget;

    if (!file) {
      setError('Сначала выберите файл.');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      await api.uploadApplicationAttachment(
        applicationId,
        file,
        description.trim(),
      );

      setFile(null);
      setDescription('');
      form.reset();

      const result = await loadAttachments();
      setAttachments(result);

      setMessage('Документ успешно загружен.');
      onUploaded?.();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Не удалось загрузить документ.',
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="loan-card" style={{ marginTop: 24 }}>
      <h2>Документы заявки</h2>

      <p>
        Форматы: PDF, PNG, JPG, DOCX. Максимальный размер — 10 МБ.
      </p>

      <form className="loan-form" onSubmit={handleUpload}>
        <div className="form-group">
          <label htmlFor="attachment-file">Файл</label>

          <input
            id="attachment-file"
            className="reg-input"
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,.docx"
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null);
              setError('');
              setMessage('');
            }}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="attachment-description">
            Описание
          </label>

          <input
            id="attachment-description"
            className="reg-input"
            type="text"
            value={description}
            onChange={(event) =>
              setDescription(event.target.value)
            }
            maxLength={500}
            placeholder="Например, бухгалтерская отчётность"
          />
        </div>

        {error && <p role="alert">{error}</p>}
        {message && <p role="status">{message}</p>}

        <button
          className="btn-submit"
          type="submit"
          disabled={loading || !file}
        >
          {loading ? 'Загрузка...' : 'Загрузить документ'}
        </button>
      </form>

      <h3 style={{ marginTop: 24 }}>Загруженные файлы</h3>

      {listLoading ? (
        <p>Загрузка списка документов...</p>
      ) : attachments.length === 0 ? (
        <p>Документы пока не добавлены.</p>
      ) : (
        <ul>
          {attachments.map((attachment) => (
            <li
              key={attachment.id}
              style={{ marginBottom: 12 }}
            >
              <strong>{attachment.filename}</strong>

              {attachment.description && (
                <p>{attachment.description}</p>
              )}

              <p>Статус: {attachment.status}</p>

              <small>
                {new Date(
                  attachment.uploaded_at,
                ).toLocaleString('ru-RU')}
              </small>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
};
