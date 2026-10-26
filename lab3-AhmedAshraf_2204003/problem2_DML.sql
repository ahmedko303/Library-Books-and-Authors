USE library;

INSERT INTO author (author_id, name, country) VALUES
  (1, 'Naguib Mahfouz',          'Egypt'),
  (2, 'Jane Austen',             'United Kingdom'),
  (3, 'Gabriel Garcia Marquez',  'Colombia'),
  (4, 'Haruki Murakami',         'Japan');

INSERT INTO book (book_id, title, price, author_id) VALUES
  (1, 'Palace Walk',               14.50, 1),
  (2, 'Midaq Alley',               11.00, 1),
  (3, 'Pride and Prejudice',        9.99, 2),
  (4, 'Emma',                      10.50, 2),
  (5, 'One Hundred Years of Solitude', 16.75, 3),
  (6, 'Love in the Time of Cholera',   15.25, 3),
  (7, 'Norwegian Wood',            13.00, 4),
  (8, 'Kafka on the Shore',        17.90, 4);
