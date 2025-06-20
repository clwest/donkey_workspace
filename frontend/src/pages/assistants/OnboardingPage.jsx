import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import apiFetch from '@/utils/apiClient';
import ThemeSelector from '../../components/onboarding/ThemeSelector';

export default function OnboardingPage() {
  const [name, setName] = useState('');
  const [specialty, setSpecialty] = useState('fantasy');
  const navigate = useNavigate();
  const [saving, setSaving] = useState(false);
  const { t } = useTranslation();

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await apiFetch('/assistants/', {
        method: 'POST',
        body: { name, specialty },
      });
      if (res && res.slug) {
        navigate(`/assistants/${res.slug}`);
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container my-4">
      <h1 className="mb-3">{t('onboarding.title')}</h1>
      <ThemeSelector specialty={specialty} onChange={setSpecialty} />
      <form onSubmit={handleCreate} style={{ maxWidth: 400 }}>
        <div className="mb-3">
          <label className="form-label">{t('onboarding.name')}</label>
          <input
            className="form-control"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <button className="btn btn-success" disabled={saving} type="submit">
          {saving ? t('onboarding.creating') : t('onboarding.create')}
        </button>
      </form>
    </div>
  );
}
