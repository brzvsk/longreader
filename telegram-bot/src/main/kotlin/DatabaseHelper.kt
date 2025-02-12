package goldenluk.readlaterbpt

import com.mongodb.client.MongoClient
import com.mongodb.client.MongoDatabase
import com.mongodb.client.model.Filters
import com.mongodb.client.model.Updates
import org.bson.conversions.Bson
import org.litote.kmongo.*

private var client: MongoClient? = null
private var database: MongoDatabase? = null

class DatabaseHelper {

    fun initClient() {
        client = KMongo.createClient("mongodb://mongodb:27017")
        database = client?.getDatabase("myBotDB")
        println("client and database set up")
    }

    fun addBookmark(userId: String, bookmark: Bookmark, userName: String) {
        if (database == null || client == null) {
            initClient()
        }
        val usersCollection = database?.getCollection<User>("users") ?: return
        val user = usersCollection.findOne(User::_id eq userId)
        if (user == null) {
            println("User with ID $userId not found.")
            usersCollection.insertOne(User(userId, userName, mutableListOf()))
        }

        val result = usersCollection.updateOne(
            User::_id eq userId,
            addToSet(User::bookmarks, bookmark)
        )
        println("Bookmark added, modified count: ${result.modifiedCount}")
    }

    fun getBookmarks(userId: String): List<Bookmark>? {
        if (database == null || client == null) {
            initClient()
        }
        val usersCollection = database?.getCollection<User>("users") ?: return emptyList()
        val user = usersCollection.findOne(User::_id eq userId)
        return user?.bookmarks
    }

    fun getUsers(): List<User> {
        if (database == null || client == null) {
            initClient()
        }

        val users = database?.getCollection<User>("users") ?: return emptyList()
        return users.find().toList()
    }

    fun removeAllBookmarks(userId: String) {
        if (database == null || client == null) {
            initClient()
        }
        val usersCollection = database?.getCollection<User>("users") ?: return

        val result = usersCollection.updateOne(
            User::_id eq userId,
            setValue(User::bookmarks, emptyList<Bookmark>())
        )

        if (result.matchedCount > 0) {
            println("Successfully removed all bookmarks for user: $userId")
        } else {
            println("User with ID $userId not found.")
        }
    }

    fun removeBookmark(userId: String, bookmarkId: String) {
        val usersCollection = database?.getCollection<User>("users") ?: return

        val update: Bson = Updates.pull("bookmarks", org.bson.Document("id", bookmarkId))

        val result = usersCollection.updateOne(User::_id eq userId, update)

        if (result.modifiedCount > 0) {
            println("Bookmark with ID $bookmarkId removed for user: $userId")
        } else {
            println("Bookmark not found or user does not exist.")
        }
    }
}