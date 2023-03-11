# Database model documentation

We use the tickets_plus schema.

## Guild Table

The `general_configs` table is used to store general configuration information for the `Tickets-Plus` bot. It includes the following columns:

| Column Name | Data Type | Primary Key | Nullable | Description |
| ----------- | --------- | -----------| -------- | ----------- |
| guild_id | Integer | Yes | No | The unique ID of the guild |
| open_message | String | No | No | The message displayed to users when a new ticket is opened. Default value is "Staff notes for Ticket $channel." |
| staff_team_name | String | No | No | The name of the staff team. Default value is "Staff Team." |
| msg_discovery | Boolean | No | No | A boolean value that indicates whether or not the bot should announce new tickets in the guild. |
| strip_buttons | Boolean | No | No | A boolean value that indicates whether or not the bot should remove the reaction buttons from messages in tickets. |

The table also includes the following relationships:

| Relationship | Description |
| ------------ | ----------- |
| ticket_users | A one-to-many relationship with the `TicketUser` table. |
| staff_roles | A one-to-many relationship with the `StaffRole` table. |
| observers_roles | A one-to-many relationship with the `ObserversRole` table. |
| community_roles | A one-to-many relationship with the `CommunityRole` table. |
| community_pings | A one-to-many relationship with the `CommunityPing` table. |
| members | A one-to-many relationship with the `Member` table. |

## TicketUser Table

The `ticket_users` table is used to store information about users who have opened tickets. It includes the following columns:

| Column Name | Data Type | Primary Key | Nullable | Description |
| ----------- | --------- | -----------| -------- | ----------- |
| user_id | Integer | Yes | No | The unique ID of the user who opened the ticket. |
| guild_id | Integer | No | No | The ID of the guild in which the ticket was opened. Foreign key to the `general_configs.guild_id` column. |

The table also includes the following relationship:

| Relationship | Description |
| ------------ | ----------- |
| guild | A many-to-one relationship with the `Guild` table. |

Note that the `guild` relationship is lazy-loaded using the `selectin` strategy.

## StaffRole Table

The `staff_roles` table is used to store information about staff roles in the guild. It includes the following columns:

| Column Name | Data Type | Primary Key | Nullable | Description |
| ----------- | --------- | -----------| -------- | ----------- |
| role_id | Integer | Yes | No | The unique ID of the staff role. |
| guild_id | Integer | No | No | The ID of the guild to which the staff role belongs. Foreign key to the `general_configs.guild_id` column. |

The table also includes the following relationship:

| Relationship | Description |
| ------------ | ----------- |
| guild | A many-to-one relationship with the `Guild` table. |

Note that the `guild` relationship is lazy-loaded using the `selectin` strategy.

## ObserversRole Table

The `observers_roles` table is used to store information about observer roles in the guild. It includes the following columns:

| Column Name | Data Type | Primary Key | Nullable | Description |
| ----------- | --------- | -----------| -------- | ----------- |
| role_id | Integer | Yes | No | The unique ID of the observer role. |
| guild_id | Integer | No | No | The ID of the guild to which the observer role belongs. Foreign key to the `general_configs.guild_id` column. |

The table also includes the following relationship:

| Relationship | Description |
| ------------ | ----------- |
| guild | A many-to-one relationship with the `Guild` table. |

Note that the `guild` relationship is lazy-loaded using the `selectin` strategy.

## CommunityRole Table

The `community_roles` table is used to store information about community roles in the guild. It includes the following columns:

| Column Name | Data Type | Primary Key | Nullable | Description |
| ----------- | --------- | -----------| -------- | ----------- |
| role_id | Integer | Yes | No | The unique ID of the community role. |
| guild_id | Integer | No | No | The ID of the guild to which the community role belongs. Foreign key to the `general_configs.guild_id` column. |

The table also includes the following relationship:

| Relationship | Description |
| ------------ | ----------- |
| guild | A many-to-one relationship with the `Guild` table. |

Note that the `guild` relationship is lazy-loaded using the `selectin` strategy.

## CommunityPing Table

The `community_pings` table is used to store information about community pings in the guild. It includes the following columns:

| Column Name | Data Type | Primary Key | Nullable | Description |
| ----------- | --------- | -----------| -------- | ----------- |
| role_id | Integer | Yes | No | The unique ID of the role that is being pinged. |
| guild_id | Integer | No | No | The ID of the guild to which the role belongs. Foreign key to the `general_configs.guild_id` column. |

The table also includes the following relationship:

| Relationship | Description |
| ------------ | ----------- |
| guild | A many-to-one relationship with the `Guild` table. |

Note that the `guild` relationship is lazy-loaded using the `selectin` strategy.

## Member Table

The `members` table is used to store information about users in the guild. It includes the following columns:

| Column Name | Data Type | Primary Key | Nullable | Description |
| ----------- | --------- | -----------| -------- | ----------- |
| id | Integer | Yes | No | The unique ID of the member. |
| user_id | Integer | No | No | The ID of the Discord user. |
| guild_id | Integer | No | No | The ID of the guild to which the user belongs. Foreign key to the `general_configs.guild_id` column. |

The table also includes the following relationship:

| Relationship | Description |
| ------------ | ----------- |
| guild | A many-to-one relationship with the `Guild` table. |

Note that the `guild` relationship is lazy-loaded using the `selectin` strategy.

In addition, the table includes the following toggle column:

| Column Name | Data Type | Default | Nullable | Description |
| ----------- | --------- | ------- | -------- | ----------- |
| is_owner | Boolean | False | No | Indicates whether the user is an owner of the bot. |
