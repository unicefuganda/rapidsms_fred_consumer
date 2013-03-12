Feature: Fred API

  Scenario: Error
    Given I try to create an invalid facility
    Then an error is returned

  Scenario: Create
    Given I have created a facility
    Then it should appear at the top of the feed
    Then I should be able to read it

  Scenario: Update
    Given I have created a facility
    Then it should appear at the top of the feed
    And I should be able to update it
    Then I should be able to read it
