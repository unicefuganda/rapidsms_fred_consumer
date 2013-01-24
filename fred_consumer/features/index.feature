Feature: Fred Configuration page

  Scenario: Landing page
    Given I am logged in
    Given I have no configurations stored
    Given I am on the Fred landing page
    Then I should see all the fields

  Scenario: Landing page - Values populated
    Given I have my fred settings added
    And I am on the Fred landing page
    Then I should see all the fields populated with values

  Scenario: Landing page - Update Configuration
    Given I have no configurations stored
    And I am on the Fred landing page
    And I enter new configurations
    Then I should see all the fields populated with values
    And I should see success message
    And I change the configurations
    Then I should see all the fields populated with values
    And I should see success message