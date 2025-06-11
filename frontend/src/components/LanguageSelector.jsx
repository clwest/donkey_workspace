import { useTranslation } from 'react-i18next';

export default function LanguageSelector() {
  const { i18n } = useTranslation();
  const changeLang = (e) => i18n.changeLanguage(e.target.value);

  return (
    <select
      aria-label="Language"
      className="form-select form-select-sm me-2"
      value={i18n.language}
      onChange={changeLang}
    >
      <option value="en">English</option>
      <option value="es">Español</option>
    </select>
  );
}
