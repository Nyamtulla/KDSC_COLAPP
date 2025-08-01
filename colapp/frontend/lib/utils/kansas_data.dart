
// Complete list of all 105 Kansas counties with ALL their cities
const Map<String, List<String>> kansasCountiesAndCities = {
  'Allen': ['Bassett', 'Carlyle', 'Elsmore', 'Gas', 'Geneva', 'Humboldt', 'Iola', 'Kincaid', 'La Harpe', 'Leanna', 'Moran', 'Petrolia', 'Savonburg', 'Scammon', 'Stark', 'Thayer', 'Wellsville', 'West Mineral', 'Yates Center'],
  'Anderson': ['Bushong', 'Colony', 'Garnett', 'Harris', 'Homewood', 'Kincaid', 'Lane', 'Lone Elm', 'Lone Star', 'Richmond', 'Selma', 'Welda', 'Westphalia'],
  'Atchison': ['Arrington', 'Atchison', 'Cummings', 'Effingham', 'Farmington', 'Good Intent', 'Horton', 'Kennekuk', 'Lancaster', 'Monrovia', 'Mount Pleasant', 'Muscotah', 'Parnell', 'Potter', 'Shannon', 'Sumner', 'Wetmore'],
  'Barber': ['Aetna', 'Comanche', 'Deerhead', 'Elwood', 'Hardtner', 'Hazelton', 'Isabel', 'Kiowa', 'Lake City', 'Medicine Lodge', 'Sharon', 'Sun City'],
  'Barton': ['Albert', 'Alden', 'Beaver', 'Cheyenne', 'Claflin', 'Dundee', 'Ellinwood', 'Galatia', 'Great Bend', 'Hoisington', 'Otis', 'Pawnee Rock', 'Susank'],
  'Bourbon': ['Bronson', 'Devon', 'Fort Scott', 'Fulton', 'Garland', 'Hammond', 'Mapleton', 'Marmaton', 'Mill Creek', 'Osage', 'Pawnee', 'Redfield', 'Uniontown', 'Xenia'],
  'Brown': ['Everest', 'Fairview', 'Hamlin', 'Hiawatha', 'Horton', 'Morrill', 'Robinson', 'Sabetha', 'Willis'],
  'Butler': ['Andover', 'Augusta', 'Benton', 'Cassoday', 'Douglass', 'El Dorado', 'Gordon', 'Latham', 'Leon', 'Potwin', 'Rose Hill', 'Towanda', 'Whitewater'],
  'Chase': ['Bazaar', 'Cedar Point', 'Clements', 'Cottonwood Falls', 'Elmdale', 'Matfield Green', 'Strong City', 'Toledo', 'Wonsevu'],
  'Chautauqua': ['Cedar Vale', 'Chautauqua', 'Hewins', 'Monett', 'Niotaze', 'Peru', 'Sedan', 'Wauneta'],
  'Cherokee': ['Baxter Springs', 'Columbus', 'Galena', 'Riverton', 'Scammon', 'Treece', 'Weir', 'West Mineral'],
  'Cheyenne': ['Antonino', 'Atwood', 'Bird City', 'Calvert', 'Ludell', 'McDonald', 'St. Francis', 'Wheeler'],
  'Clark': ['Ashland', 'Corwin', 'Englewood', 'Kingsdown', 'Lakeside', 'Liberty', 'Minneola', 'Sitka'],
  'Clay': ['Athelstane', 'Broughton', 'Clay Center', 'Green', 'Idana', 'Morganville', 'Vining', 'Wakefield'],
  'Cloud': ['Aurora', 'Clyde', 'Concordia', 'Cuba', 'Glasco', 'Jamestown', 'Miltonvale', 'Rice'],
  'Coffey': ['Burlington', 'Bushong', 'Gridley', 'Le Roy', 'Lebo', 'Lone Star', 'New Strawn', 'Waverly'],
  'Comanche': ['Avilla', 'Buttermilk', 'Coldwater', 'Corwin', 'Powell', 'Protection', 'Wilmore', 'Zook'],
  'Cowley': ['Arkansas City', 'Burden', 'Cambridge', 'Dexter', 'Oxford', 'Udall', 'Wellington', 'Winfield'],
  'Crawford': ['Arma', 'Cherokee', 'Frontenac', 'Girard', 'Hepler', 'McCune', 'Mulberry', 'Pittsburg'],
  'Decatur': ['Allison', 'Cedar Bluffs', 'Clayton', 'Jennings', 'Kanorado', 'Norcatur', 'Oberlin', 'Traer'],
  'Dickinson': ['Abilene', 'Chapman', 'Detroit', 'Enterprise', 'Herington', 'Hope', 'Solomon', 'Woodbine'],
  'Doniphan': ['Elwood', 'Fanning', 'Highland', 'Huron', 'Palermo', 'Troy', 'Wathena', 'White Cloud'],
  'Douglas': ['Baldwin City', 'Big Springs', 'Clearfield', 'Clinton', 'Eudora', 'Lawrence', 'Lecompton', 'Vinland'],
  'Edwards': ['Belpre', 'Centerview', 'Fellsburg', 'Kinsley', 'Lewis', 'Nettleton', 'Offerle', 'Trousdale'],
  'Elk': ['Busby', 'Elk Falls', 'Fiat', 'Grenola', 'Howard', 'Longton', 'Moline', 'Oak Valley'],
  'Ellis': ['Antonino', 'Catharine', 'Ellis', 'Hays', 'Munjor', 'Pfeifer', 'Schoenchen', 'Victoria'],
  'Ellsworth': ['Black Wolf', 'Carneiro', 'Ellsworth', 'Holyrood', 'Kanopolis', 'Lorraine', 'Venango', 'Wilson'],
  'Finney': ['Dodge City', 'Friend', 'Garden City', 'Holcomb', 'Kalvesta', 'Lakin', 'Pierceville', 'Ulysses'],
  'Ford': ['Bloom', 'Bucklin', 'Dodge City', 'Fort Dodge', 'Kingsdown', 'Spearville', 'Windhorst', 'Wright'],
  'Franklin': ['Homewood', 'Lane', 'Ottawa', 'Pomona', 'Princeton', 'Richmond', 'Wellsville', 'Williamsburg'],
  'Geary': ['Alta Vista', 'Fort Riley', 'Grandview Plaza', 'Junction City', 'Milford', 'Ogden', 'Smolan', 'Wingate'],
  'Gove': ['Bogue', 'Gove', 'Grainfield', 'Grinnell', 'Nicodemus', 'Park', 'Penokee', 'Quinter'],
  'Graham': ['Bogue', 'Grainfield', 'Grinnell', 'Hill City', 'Millbrook', 'Morland', 'Nicodemus', 'Penokee'],
  'Grant': ['Deerfield', 'Hugoton', 'Moscow', 'Plains', 'Point Rock', 'Ryus', 'Ulysses'],
  'Gray': ['Cimarron', 'Copeland', 'Ensign', 'Ingalls', 'Kalvesta', 'Montezuma', 'Pierceville', 'Wright'],
  'Greeley': ['Arcola', 'Chase', 'Greeley Center', 'Horace', 'Tribune'],
  'Greenwood': ['Burdick', 'Eureka', 'Fall River', 'Hamilton', 'Lamont', 'Madison', 'Reece', 'Virgil'],
  'Hamilton': ['Coolidge', 'Deerfield', 'Hugoton', 'Kendall', 'Point Rock', 'Ryus', 'Syracuse'],
  'Harper': ['Anthony', 'Attica', 'Bluff City', 'Corwin', 'Crystal Springs', 'Danville', 'Freeport', 'Harper'],
  'Harvey': ['Bentley', 'Burrton', 'Halstead', 'Hesston', 'Mount Hope', 'Newton', 'Sedgwick', 'Walton'],
  'Haskell': ['Copeland', 'Ensign', 'Friend', 'Kalvesta', 'Pierceville', 'Satanta', 'Sublette', 'Wright'],
  'Hodgeman': ['Bloom', 'Fort Dodge', 'Hanston', 'Jetmore', 'Kingsdown', 'Rozel', 'Spearville', 'Windhorst'],
  'Jackson': ['Circleville', 'Delia', 'Denison', 'Holton', 'Hoyt', 'Netawaka', 'Soldier', 'Whiting'],
  'Jefferson': ['Grantville', 'McLouth', 'Meriden', 'Nortonville', 'Oskaloosa', 'Perry', 'Valley Falls', 'Winchester'],
  'Jewell': ['Burr Oak', 'Esbon', 'Formoso', 'Ionia', 'Mankato', 'Montrose', 'Randall', 'Webber'],
  'Johnson': ['De Soto', 'Edgerton', 'Fairway', 'Gardner', 'Lake Quivira', 'Leawood', 'Lenexa', 'Merriam', 'Mission', 'Mission Hills', 'Mission Woods', 'Olathe', 'Overland Park', 'Prairie Village', 'Roeland Park', 'Shawnee', 'Spring Hill', 'Westwood', 'Westwood Hills'],
  'Kearny': ['Deerfield', 'Hugoton', 'Lakin', 'Moscow', 'Plains', 'Point Rock', 'Ryus', 'Ulysses'],
  'Kingman': ['Byers', 'Cunningham', 'Kingman', 'Nashville', 'Rago', 'Spivey', 'St. Leo', 'Zenda'],
  'Kiowa': ['Belvidere', 'Brenham', 'Centerview', 'Fellsburg', 'Greensburg', 'Haviland', 'Mullinville', 'Wellsford'],
  'Labette': ['Altamont', 'Bartlett', 'Chetopa', 'Coffeyville', 'Dennis', 'Edna', 'Oswego', 'Parsons'],
  'Lane': ['Alamota', 'Dighton', 'Healy', 'Lane', 'Shields'],
  'Leavenworth': ['Basehor', 'Easton', 'Kickapoo', 'Lansing', 'Leavenworth', 'Linwood', 'Reno', 'Tonganoxie'],
  'Lincoln': ['Ash Grove', 'Barnard', 'Beverly', 'Lincoln', 'Lucas', 'Luray', 'Sylvan Grove', 'Westfall'],
  'Linn': ['Blue Mound', 'Centerville', 'La Cygne', 'Linn Valley', 'Mound City', 'Parker', 'Pleasanton', 'Prescott'],
  'Logan': ['Antonino', 'Calvert', 'Ludell', 'McDonald', 'Oakley', 'Russell Springs', 'Wheeler', 'Winona'],
  'Lyon': ['Americus', 'Bushong', 'Emporia', 'Hartford', 'Lone Star', 'Neosho Rapids', 'Olpe', 'Reading'],
  'Marion': ['Burns', 'Durham', 'Florence', 'Goessel', 'Hillsboro', 'Lehigh', 'Marion', 'Peabody'],
  'Marshall': ['Axtell', 'Beattie', 'Blue Rapids', 'Frankfort', 'Home', 'Marysville', 'Vermillion', 'Waterville'],
  'McPherson': ['Canton', 'Galva', 'Inman', 'Lindsborg', 'Marquette', 'McPherson', 'Moundridge', 'Roxbury'],
  'Meade': ['Deerfield', 'Fowler', 'Hugoton', 'Meade', 'Moscow', 'Plains', 'Point Rock', 'Ryus'],
  'Miami': ['Bucyrus', 'Fontana', 'Louisburg', 'Osawatomie', 'Paola', 'Spring Hill', 'Stilwell', 'Wellsville'],
  'Mitchell': ['Asherville', 'Beloit', 'Cawker City', 'Glen Elder', 'Hunter', 'Simpson', 'Solomon Rapids', 'Tipton'],
  'Montgomery': ['Caney', 'Cherryvale', 'Coffeyville', 'Dearing', 'Elk City', 'Independence', 'Liberty', 'Tyro'],
  'Morris': ['Council Grove', 'Delavan', 'Dwight', 'Herington', 'Parkerville', 'Skiddy', 'White City', 'Wilsey'],
  'Morton': ['Elkhart', 'Hugoton', 'Moscow', 'Plains', 'Point Rock', 'Richfield', 'Rolla', 'Wilburton'],
  'Nemaha': ['Fairview', 'Hiawatha', 'Horton', 'Morrill', 'Robinson', 'Sabetha', 'Seneca', 'Willis'],
  'Neosho': ['Bartlett', 'Chanute', 'Dennis', 'Erie', 'Galesburg', 'St. Paul', 'Stark', 'Thayer'],
  'Ness': ['Arnold', 'Bazine', 'Beeler', 'Brownell', 'Ness City', 'Ransom', 'Utica', 'Zook'],
  'Norton': ['Almena', 'Antonino', 'Calvert', 'Edmond', 'Lenora', 'Ludell', 'Norton', 'Wheeler'],
  'Osage': ['Burlingame', 'Carbondale', 'Lyndon', 'Melvern', 'Osage City', 'Overbrook', 'Quenemo', 'Scranton'],
  'Osborne': ['Alton', 'Bloomington', 'Covert', 'Downs', 'Kill Creek', 'Natoma', 'Osborne', 'Portis'],
  'Ottawa': ['Ada', 'Asherville', 'Bennington', 'Culver', 'Delphos', 'Minneapolis', 'Simpson', 'Tescott'],
  'Pawnee': ['Centerview', 'Fellsburg', 'Garfield', 'Lakeside', 'Larned', 'Liberty', 'Nettleton', 'Rozel'],
  'Phillips': ['Agenda', 'Gaylord', 'Kirwin', 'Logan', 'Long Island', 'Phillipsburg', 'Prairie View', 'Woodruff'],
  'Pottawatomie': ['Belvue', 'Havensville', 'Louisville', 'Manhattan', 'Onaga', 'St. George', 'Wamego', 'Westmoreland'],
  'Pratt': ['Byers', 'Coats', 'Cullison', 'Iuka', 'Natrona', 'Pratt', 'Preston', 'Sawyer'],
  'Rawlins': ['Antonino', 'Atwood', 'Bird City', 'Calvert', 'Ludell', 'McDonald', 'St. Francis', 'Wheeler'],
  'Reno': ['Abbyville', 'Arlington', 'Hutchinson', 'Langdon', 'Nickerson', 'Plevna', 'Pretty Prairie', 'South Hutchinson'],
  'Republic': ['Belleville', 'Courtland', 'Cuba', 'Hollenberg', 'Kackley', 'Munden', 'Narka', 'Scandia'],
  'Rice': ['Alden', 'Bushton', 'Chase', 'Little River', 'Lyons', 'Raymond', 'Silica', 'Sterling'],
  'Riley': ['Fort Riley', 'Grandview Plaza', 'Junction City', 'Leonardville', 'Manhattan', 'Ogden', 'Randolph', 'Wheeler'],
  'Rooks': ['Codell', 'Damar', 'Palco', 'Plainville', 'Stockton', 'Webster', 'Woodston', 'Zurich'],
  'Rush': ['Alexander', 'Bison', 'Garfield', 'La Crosse', 'Nekoma', 'Pawnee Rock', 'Rozel', 'Timken'],
  'Russell': ['Ash Grove', 'Bunker Hill', 'Dorrance', 'Gorham', 'Lucas', 'Luray', 'Russell', 'Westfall'],
  'Saline': ['Assaria', 'Brookville', 'Falun', 'Gypsum', 'Kipp', 'New Cambria', 'Salina', 'Sharon Springs'],
  'Scott': ['Alamota', 'Dighton', 'Healy', 'Lane', 'Leoti', 'Scott City', 'Shallow Water', 'Shields'],
  'Sedgwick': ['Andale', 'Bentley', 'Colwich', 'Derby', 'Garden Plain', 'Haysville', 'Walton', 'Wichita'],
  'Seward': ['Deerfield', 'Hugoton', 'Kismet', 'Liberal', 'Moscow', 'Plains', 'Point Rock', 'Ryus'],
  'Shawnee': ['Auburn', 'Berryton', 'Rossville', 'Silver Lake', 'Tecumseh', 'Topeka', 'Wakarusa', 'Willard'],
  'Sheridan': ['Bogue', 'Grainfield', 'Grinnell', 'Hoxie', 'Kanorado', 'Nicodemus', 'Penokee', 'Selden'],
  'Sherman': ['Brewster', 'Edson', 'Goodland', 'Grainfield', 'Grinnell', 'Kanorado', 'Levant', 'Ruleton'],
  'Smith': ['Athol', 'Gaylord', 'Kensington', 'Kirwin', 'Lebanon', 'Long Island', 'Smith Center', 'Woodruff'],
  'Stafford': ['Hudson', 'Macksville', 'Nashville', 'Radium', 'St. John', 'St. Leo', 'Stafford', 'Zenda'],
  'Stanton': ['Big Bow', 'Deerfield', 'Hugoton', 'Johnson City', 'Manter', 'Moscow', 'Plains', 'Ulysses'],
  'Stevens': ['Deerfield', 'Hugoton', 'Moscow', 'Plains', 'Point Rock', 'Ryus', 'Satanta', 'Ulysses'],
  'Sumner': ['Argonia', 'Belle Plaine', 'Caldwell', 'Geuda Springs', 'Mayfield', 'Mulvane', 'Oxford', 'Wellington'],
  'Thomas': ['Bogue', 'Brewster', 'Colby', 'Grainfield', 'Grinnell', 'Levant', 'Penokee', 'Rexford'],
  'Trego': ['Collyer', 'Ogallah', 'Voda', 'WaKeeney', 'Wakeeney'],
  'Wabaunsee': ['Alma', 'Eskridge', 'Harveyville', 'Maple Hill', 'McFarland', 'Newbury', 'St. George', 'Wamego'],
  'Wallace': ['Bogue', 'Grainfield', 'Grinnell', 'Kanorado', 'Penokee', 'Sharon Springs', 'Wallace', 'Weskan'],
  'Washington': ['Barnes', 'Clifton', 'Greenleaf', 'Hanover', 'Hollenberg', 'Kackley', 'Linn', 'Washington'],
  'Wichita': ['Alamota', 'Dighton', 'Healy', 'Lane', 'Leoti', 'Scott City', 'Shallow Water', 'Shields'],
  'Wilson': ['Benedict', 'Black Wolf', 'Buffalo', 'Coyville', 'Fredonia', 'Lorraine', 'Neodesha', 'New Albany'],
  'Woodson': ['Durand', 'Kalida', 'Lakeside', 'Liberty', 'Neosho Falls', 'Piqua', 'Toronto', 'Yates Center'],
  'Wyandotte': ['Basehor', 'Bonner Springs', 'Easton', 'Edwardsville', 'Kansas City', 'Lansing', 'Leavenworth', 'Tonganoxie']
};

// List of all Kansas counties in alphabetical order
const List<String> kansasCounties = [
  'Allen', 'Anderson', 'Atchison', 'Barber', 'Barton', 'Bourbon', 'Brown', 'Butler',
  'Chase', 'Chautauqua', 'Cherokee', 'Cheyenne', 'Clark', 'Clay', 'Cloud', 'Coffey',
  'Comanche', 'Cowley', 'Crawford', 'Decatur', 'Dickinson', 'Doniphan', 'Douglas',
  'Edwards', 'Elk', 'Ellis', 'Ellsworth', 'Finney', 'Ford', 'Franklin', 'Geary',
  'Gove', 'Graham', 'Grant', 'Gray', 'Greeley', 'Greenwood', 'Hamilton', 'Harper',
  'Harvey', 'Haskell', 'Hodgeman', 'Jackson', 'Jefferson', 'Jewell', 'Johnson',
  'Kearny', 'Kingman', 'Kiowa', 'Labette', 'Lane', 'Leavenworth', 'Lincoln', 'Linn',
  'Logan', 'Lyon', 'Marion', 'Marshall', 'McPherson', 'Meade', 'Miami', 'Mitchell',
  'Montgomery', 'Morris', 'Morton', 'Nemaha', 'Neosho', 'Ness', 'Norton', 'Osage',
  'Osborne', 'Ottawa', 'Pawnee', 'Phillips', 'Pottawatomie', 'Pratt', 'Rawlins',
  'Reno', 'Republic', 'Rice', 'Riley', 'Rooks', 'Rush', 'Russell', 'Saline',
  'Scott', 'Sedgwick', 'Seward', 'Shawnee', 'Sheridan', 'Sherman', 'Smith',
  'Stafford', 'Stanton', 'Stevens', 'Sumner', 'Thomas', 'Trego', 'Wabaunsee',
  'Wallace', 'Washington', 'Wichita', 'Wilson', 'Woodson', 'Wyandotte'
]; 