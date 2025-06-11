import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';
import OnboardingPage from '../pages/assistants/OnboardingPage';

describe('i18n', () => {
  it('switches to Spanish', () => {
    i18n.changeLanguage('es');
    const { getByText } = render(
      <I18nextProvider i18n={i18n}>
        <OnboardingPage />
      </I18nextProvider>
    );
    expect(getByText('Crea tu primer asistente')).toBeTruthy();
  });
});
