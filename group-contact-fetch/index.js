const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs/promises');

const CHAT_FILE = '../data/chats.json';
const CONTACT_FILE = '../data/contact.json';

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: { 
        // args: ['--proxy-server=proxy-server-that-requires-authentication.example.com'],
        headless: false
    }
});

client.on('qr', (qr) => {
    // Generate and scan this code with your phone
    console.log('QR RECEIVED', qr);

    qrcode.generate(qr, {small: true});
});

client.on('ready', async () => {
    console.log('Client is ready!');

    const chats = await client.getChats();
    await fs.writeFile(CHAT_FILE, JSON.stringify(chats));
    console.log(`Chats file saved at '${CHAT_FILE}'. Chats: ${chats.length}`);

    const contacts = await client.getContacts()
    await fs.writeFile(CONTACT_FILE, JSON.stringify(contacts));
    console.log(`Contacts file saved at '${CONTACT_FILE}'. Contacts: ${contacts.length}`);

    process.exit();
});

client.on('message', msg => {
    if (msg.body == '!ping') {
        msg.reply('pong');
    }
});

client.initialize();