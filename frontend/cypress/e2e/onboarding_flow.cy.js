// Cypress E2E outline for onboarding flow
// Log in, visit onboarding page, create assistant, verify redirect

it('creates assistant via onboarding', () => {
  cy.login();
  cy.visit('/assistants/onboarding');
  cy.get('input').type('Cypress Helper');
  cy.contains('Create').click();
  cy.url().should('include', '/assistants/');
});
