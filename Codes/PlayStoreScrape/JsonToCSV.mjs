import axios from 'axios';
import { parse } from 'json2csv';
import fs from 'fs';
import path from 'path';

const __dirname = path.dirname(new URL(import.meta.url).pathname);
const dataFolderPath = path.join(__dirname, '../../Data');

// Create the data folder if it doesn't exist
if (!fs.existsSync(dataFolderPath)) {
  fs.mkdirSync(dataFolderPath, { recursive: true });
}

// Make a GET request to your localhost server
axios.get('http://localhost:3000/api/apps/sg.com.gxs.app/reviews/')
  .then(response => {
    const jsonData = response.data.results.data; // Extract data from the 'results' object

    // Check if there is data to convert
    if (jsonData.length === 0) {
      console.log('No data to convert to CSV.');
      return;
    }

    // Define the fields for CSV conversion
    const fields = [
      'id',
      'userName',
      'userImage',
      'date',
      'score',
      'scoreText',
      'url',
      'title',
      'text',
      'replyDate',
      'replyText',
      'version',
      'thumbsUp',
      'criterias'
    ];

    // Convert JSON data to CSV format
    const csvData = parse(jsonData, { fields });

    // Define the full path for the CSV file using path.join
    const filePath = decodeURIComponent(path.join(dataFolderPath, 'PlayStoreData.csv'));

    // Write CSV data to the specified file path
    fs.writeFileSync(filePath, csvData);
    console.log('CSV file created successfully at:', filePath);
  })
  .catch(error => {
    console.error('Error fetching data:', error);
  });
