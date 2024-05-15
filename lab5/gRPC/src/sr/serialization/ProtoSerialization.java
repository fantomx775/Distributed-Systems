package sr.serialization;

import java.io.FileOutputStream;
import java.io.IOException;

import sr.proto.AddressBookProtos.Person;

public class ProtoSerialization {

	public static void main(String[] args) {
		try {
			new ProtoSerialization().testProto();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	public void testProto() throws IOException {
		Person.Builder personBuilder = Person.newBuilder();
		personBuilder.setId(123456)
				.setName("Włodzimierz Wróblewski")
				.setEmail("wrobel@poczta.com")
				.addPhones(
						Person.PhoneNumber.newBuilder()
								.setNumber("+48-12-555-4321")
								.setType(Person.PhoneType.HOME))
				.addPhones(
						Person.PhoneNumber.newBuilder()
								.setNumber("+48-699-989-796")
								.setType(Person.PhoneType.MOBILE));

		// Dodanie sekwencji liczb niecałkowitych do wiadomości Person
//		personBuilder.addIncomes(1000.50f);
//		personBuilder.addIncomes(1500.75f);
//		personBuilder.addIncomes(2000.25f);

		Person p1 = personBuilder.build();

		byte[] p1ser = null;

		long n = 100000;
		System.out.println("Performing proto serialization " + n + " times...");
		long startTime = System.currentTimeMillis();
		for (long i = 0; i < n; i++) {
			p1ser = p1.toByteArray();
		}
		long stopTime = System.currentTimeMillis();
		System.out.println("... finished." + (stopTime - startTime) + " ms");

		//print data as hex values
		for (byte b : p1ser) {
			System.out.print(String.format("%02X", b));
		}

		//serialize again (only once) and write to a file
		try (FileOutputStream file = new FileOutputStream("person2.ser")) {
			file.write(p1.toByteArray());
		}
	}
}
