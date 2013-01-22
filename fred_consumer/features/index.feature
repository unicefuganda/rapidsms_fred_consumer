Feature: Fred Configuration page

  Scenario: Landing page
    Given I am on the Fred landing page
    Then I should see all the fields

  Scenario: Landing page - Values populated
    Given I have my fred settings added
    And I am on the Fred landing page
    Then I should see all the fields populated with values