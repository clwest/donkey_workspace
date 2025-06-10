// Cypress tour flow
it('runs first use tour', () => {
  cy.login();
  cy.visit('/tour');
  cy.contains('All your assistants').should('exist');
  cy.get('.react-joyride__tooltip button').contains('Next').click({ multiple: true });
  cy.contains('Track growth progress');
});
