import React, { useState } from 'react';
import * as DocumentPicker from 'expo-document-picker';
import { mobileApi } from '@untold/api';
import { Screen, Title, Card, Muted, PrimaryButton, ErrorText } from '../components/ui';

export default function UploadScreen() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const pick = async () => {
    const res = await DocumentPicker.getDocumentAsync({ copyToCacheDirectory: true });
    if (!res.canceled && res.assets?.[0]) {
      setFile(res.assets[0]);
      setResult(null);
      setError('');
    }
  };

  const upload = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const payload = {
        uri: file.uri,
        name: file.name,
        type: file.mimeType || 'application/octet-stream',
      };
      const asset = await mobileApi.studioUpload(payload);
      setResult(asset);
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <Title>Media upload</Title>
      <Card>
        <Muted>{file ? file.name : 'No file selected'}</Muted>
        <PrimaryButton title="Choose file" onPress={pick} />
      </Card>
      <PrimaryButton title={loading ? 'Uploading…' : 'Upload to library'} onPress={upload} disabled={!file || loading} />
      <ErrorText>{error}</ErrorText>
      {result && (
        <Card>
          <Muted>Uploaded: {result.filename || result.title}</Muted>
          <Muted>{result.url}</Muted>
        </Card>
      )}
    </Screen>
  );
}
